#     Copyright 2022. ThingsBoard
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

from thingsboard_gateway.connectors.converter import Converter, log
import numpy as np
import time

# byteBuffer = np.zeros(2**15, dtype='uint8')
# byteBufferLength = 0

class CustomSerialUplinkConverter(Converter):
    def __init__(self, config):
        self.__config = config
        self.result_dict = {
            'deviceName': config.get('name', 'CustomSerialDevice'),
            'deviceType': config.get('deviceType', 'default'),
            'attributes': [],
            'telemetry': []
            }
        self.byteBuffer = np.zeros(2**15, dtype='uint8')
        self.byteBufferLength = 0

    def convert(self, config, data: bytes):
        # global byteBuffer, byteBufferLength

        # Constants
        OBJ_STRUCT_SIZE_BYTES = 12;
        BYTE_VEC_ACC_MAX_SIZE = 2**15;
        MMWDEMO_UART_MSG_DETECTED_POINTS = 1;
        MMWDEMO_UART_MSG_RANGE_PROFILE   = 2;
        maxBufferSize = 2**15;
        tlvHeaderLengthInBytes = 8;
        pointLengthInBytes = 16;
        magicWord = [2, 1, 4, 3, 6, 5, 8, 7]
        
        # Initialize variables
        magicOK = 0 # Checks if magic number has been read
        dataOK = 0 # Checks if the data has been read correctly
        frameNumber = 0
        detObj = {}

        keys = ['attributes', 'telemetry']
        for key in keys:
            self.result_dict[key] = []
            if self.__config.get(key) is not None:
                for config_object in self.__config.get(key):
                    data_to_convert = data
                    # log.info("data: %s", data_to_convert)
                    byteVec = np.frombuffer(data_to_convert, dtype = 'uint8')
                    byteCount = len(byteVec)

                    # Check that the buffer is not full, and then add the data to the buffer
                    if (self.byteBufferLength + byteCount) < maxBufferSize:
                        self.byteBuffer[self.byteBufferLength:self.byteBufferLength + byteCount] = byteVec[:byteCount]
                        self.byteBufferLength = self.byteBufferLength + byteCount
                        
                    # Check that the buffer has some data
                    if self.byteBufferLength > 16:
                        
                        # Check for all possible locations of the magic word
                        possibleLocs = np.where(self.byteBuffer == magicWord[0])[0]

                        # Confirm that is the beginning of the magic word and store the index in startIdx
                        startIdx = []
                        for loc in possibleLocs:
                            check = self.byteBuffer[loc:loc+8]
                            if np.all(check == magicWord):
                                startIdx.append(loc)
                            
                        # Check that startIdx is not empty
                        if startIdx:
                            
                            # Remove the data before the first start index
                            if startIdx[0] > 0 and startIdx[0] < self.byteBufferLength:
                                self.byteBuffer[:self.byteBufferLength-startIdx[0]] = self.byteBuffer[startIdx[0]:self.byteBufferLength]
                                self.byteBuffer[self.byteBufferLength-startIdx[0]:] = np.zeros(len(self.byteBuffer[self.byteBufferLength-startIdx[0]:]),dtype = 'uint8')
                                self.byteBufferLength = self.byteBufferLength - startIdx[0]
                                
                            # Check that there have no errors with the byte buffer length
                            if self.byteBufferLength < 0:
                                self.byteBufferLength = 0
                                
                            # word array to convert 4 bytes to a 32 bit number
                            word = [1, 2**8, 2**16, 2**24]
                            
                            # Read the total packet length
                            totalPacketLen = np.matmul(self.byteBuffer[12:12+4],word)
                            
                            # Check that all the packet has been read
                            if (self.byteBufferLength >= totalPacketLen) and (self.byteBufferLength != 0):
                                magicOK = 1

                    # log.info("Magic number: %s", magicOK)
                    # If magicOK is equal to 1 then process the message
                    if magicOK:
                        # word array to convert 4 bytes to a 32 bit number
                        word = [1, 2**8, 2**16, 2**24]
                        
                        # Initialize the pointer index
                        idX = 0
                        
                        # Read the header
                        magicNumber = self.byteBuffer[idX:idX+8]
                        idX += 8
                        version = format(np.matmul(self.byteBuffer[idX:idX+4],word),'x')
                        idX += 4
                        totalPacketLen = np.matmul(self.byteBuffer[idX:idX+4],word)
                        idX += 4
                        platform = format(np.matmul(self.byteBuffer[idX:idX+4],word),'x')
                        idX += 4
                        frameNumber = np.matmul(self.byteBuffer[idX:idX+4],word)
                        idX += 4
                        timeCpuCycles = np.matmul(self.byteBuffer[idX:idX+4],word)
                        idX += 4
                        numDetectedObj = np.matmul(self.byteBuffer[idX:idX+4],word)
                        idX += 4
                        numTLVs = np.matmul(self.byteBuffer[idX:idX+4],word)
                        idX += 4
                        subFrameNumber = np.matmul(self.byteBuffer[idX:idX+4],word)
                        idX += 4

                        # Read the TLV messages
                        for tlvIdx in range(numTLVs):
                            
                            # word array to convert 4 bytes to a 32 bit number
                            word = [1, 2**8, 2**16, 2**24]

                            # Check the header of the TLV message
                            tlv_type = np.matmul(self.byteBuffer[idX:idX+4],word)
                            idX += 4
                            tlv_length = np.matmul(self.byteBuffer[idX:idX+4],word)
                            idX += 4

                            # Read the data depending on the TLV message
                            if tlv_type == MMWDEMO_UART_MSG_DETECTED_POINTS:

                                # Initialize the arrays
                                x = np.zeros(numDetectedObj,dtype=np.float32)
                                y = np.zeros(numDetectedObj,dtype=np.float32)
                                z = np.zeros(numDetectedObj,dtype=np.float32)
                                velocity = np.zeros(numDetectedObj,dtype=np.float32)
                                
                                for objectNum in range(numDetectedObj):
                                    
                                    # Read the data for each object
                                    x[objectNum] = self.byteBuffer[idX:idX + 4].view(dtype=np.float32)
                                    idX += 4
                                    y[objectNum] = self.byteBuffer[idX:idX + 4].view(dtype=np.float32)
                                    idX += 4
                                    z[objectNum] = self.byteBuffer[idX:idX + 4].view(dtype=np.float32)
                                    idX += 4
                                    velocity[objectNum] = self.byteBuffer[idX:idX + 4].view(dtype=np.float32)
                                    idX += 4
                                
                                # Store the data in the detObj dictionary
                                detObj = {"numObj": numDetectedObj, "x": x, "y": y, "z": z, "velocity":velocity}
                                dataOK = 1
                                
                
                        # Remove already processed data
                        if idX > 0 and self.byteBufferLength>idX:
                            shiftSize = totalPacketLen
                            
                                
                            self.byteBuffer[:self.byteBufferLength - shiftSize] = self.byteBuffer[shiftSize:self.byteBufferLength]
                            self.byteBuffer[self.byteBufferLength - shiftSize:] = np.zeros(len(self.byteBuffer[self.byteBufferLength - shiftSize:]),dtype = 'uint8')
                            self.byteBufferLength = self.byteBufferLength - shiftSize
                            
                            # Check that there are no errors with the buffer length
                            if self.byteBufferLength < 0:
                                self.byteBufferLength = 0         

                                        

                        now = int(round(time.time()*1000))
                        numDetectedObj_in_int = int(numDetectedObj)
                        converted_data = {config_object['key']: numDetectedObj_in_int, "ts": now, "values": {"Number of detected object:": numDetectedObj_in_int}}
                        self.result_dict[key].append(converted_data)
                        log.info("Converted data: %s", self.result_dict)
        
        return self.result_dict
