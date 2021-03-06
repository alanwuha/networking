from bitarray import bitarray
from bitarray.util import int2ba

class Udp:
    """
    UDP Segment.

    source_port: 16 bits
    destination_port: 16 bits
    length: 16 bits
    checksum: 16 bits
    data: maximum of 65,507 bytes
    """

    DATA_MAX_LENGTH = 65507
    ENCODING = 'utf-8'
    ZERO_BYTE = b'\x00'
    ENDIAN = 'big'

    def __init__(self, source_port: int, destination_port: int, data: str):
        self.source_port = source_port
        self.destination_port = destination_port
        self.checksum = 0
        self.length = 0
        self.is_valid = False
        self.set_data(data)

    def set_data(self, data: str):
        """ Sets data of UDP segment. """
        if data is None:
            raise TypeError(f"Data must not be None!")
        elif type(data) != str:
            raise TypeError(f"Data must be of type str!")
        elif len(data) > self.DATA_MAX_LENGTH:
            raise ValueError(f"Data must not be more than {self.DATA_MAX_LENGTH} characters!")
        self.data = data

    def get_length(self) -> int:
        """ Returns size of UDP segment in bytes. """
        return 64 + len(self.data)

    def get_checksum(self) -> bytearray:
        """ Returns checksum of UDP segment. """

        # Get bytearray of UDP with checksum of value of 0
        s = self.serialize(use_checksum_zero=True)
        
        # Add one more byte if data length is odd
        if len(s) % 2 != 0:
            s += self.ZERO_BYTE
        # print(s, len(s))

        return 1

    def is_checksum_valid(self) -> bool:
        return self.checksum == self.get_checksum()

    def get_bitarray(self) -> bitarray:
        """ Returns bitarray of UDP segment. """
        arr = bitarray()
        arr += int2ba(self.source_port, 16)
        arr += int2ba(self.destination_port, 16)
        arr += int2ba(self.get_length(), 16)
        arr += int2ba(self.get_checksum(), 16)

        # Convert data from string to byte array and then to bit array
        data_ba = bitarray()
        data_ba.frombytes(self.data.encode(self.ENCODING))
        arr += data_ba

        return arr

    def serialize(self, use_checksum_zero=False) -> bytearray:
        """ Returns byte array of UDP segment. """
        s = bytearray()
        checksum = 0 if use_checksum_zero else self.get_checksum()
        self.checksum = self.checksum if use_checksum_zero else checksum
        header = [self.source_port, self.destination_port, self.get_length(), checksum]
        for h in header:
            s += h.to_bytes(2, self.ENDIAN)
        s += bytearray(self.data.encode(self.ENCODING))

        return s

    def deserialize(self, b = bytearray):
        """ Deserializes bytearray and updates member variables """
        self.source_port = int.from_bytes(b[0:2], self.ENDIAN)
        self.destination_port = int.from_bytes(b[2:4], self.ENDIAN)
        self.length = int.from_bytes(b[4:6], self.ENDIAN)
        self.checksum = int.from_bytes(b[6:8], self.ENDIAN)
        self.data = b[8:].decode(self.ENCODING)
        self.is_valid = self.is_checksum_valid()

