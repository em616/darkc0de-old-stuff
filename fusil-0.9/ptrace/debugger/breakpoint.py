from ptrace.ctypes_tools import formatAddress
from ptrace import PtraceError
from logging import debug
from weakref import ref
from ptrace.cpu_info import CPU_PPC, CPU_WORD_SIZE
from ptrace.ctypes_tools import word2bytes

class Breakpoint:
    def __init__(self, process, address, size=None):
        self._installed = False
        self.process = ref(process)
        self.address = address
        if CPU_PPC:
            size = CPU_WORD_SIZE
        elif size is None:
            size = 1
        self.size = size

        # Store instruction bytes
        debug("Install %s" % self)
        self.old_bytes = process.readBytes(address, size)

        if CPU_PPC:
            # Replace instruction with "TRAP"
            new_bytes = word2bytes(0x0cc00000)
        else:
            # Replace instruction with "INT 3"
            new_bytes = "\xCC" * size
        process.writeBytes(address, new_bytes)
        self._installed = True

    def desinstall(self, set_ip=False):
        if not self._installed:
            return
        self._installed = False
        debug("Desinstall %s" % self)
        process = self.process()
        if not process:
            return
        process.writeBytes(self.address, self.old_bytes)
        if set_ip:
            process.setInstrPointer(self.address)
        process.removeBreakpoint(self)

    def __str__(self):
        return "<Breakpoint %s..%s>" % (
            formatAddress(self.address),
            formatAddress(self.address + self.size - 1))

    def __del__(self):
        try:
            self.desinstall(False)
        except PtraceError:
            pass

