import protos.example_pb2_grpc as example_pb2_grpc
from protos import example_pb2
from .utils import get_rent_by_district

class RentCalcServicer(example_pb2_grpc.MyServiceServicer):
    def SendMessage(self, request, context):
        print(f"Received message: {request.message}")
        
        return example_pb2.MessageResponse(reply=f"Hello, you said: {request.message}")
    
def register_service(server):
    example_pb2_grpc.add_MyServiceServicer_to_server(MyServiceServicer(), server)