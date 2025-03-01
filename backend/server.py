import os
import grpc
from concurrent import futures
import importlib.util
import config

# -----------------
# | LOAD SERVICES |
# -----------------
def load_services(server):
    services_dir = os.path.join(os.path.dirname(__file__), "services")
    for filename in os.listdir(services_dir):
        if filename.endswith("_service.py"):
            module_name = filename[:-3]
            module_path = os.path.join(services_dir, filename)
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "register_service"):
                print(f"Registering {module_name}...")
                module.register_service(server)
            else:
                print(f"Module {module_name} does not implement register_service.")
                
# ----------
# | SERVER |
# ----------
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(config.MAX_WORKERS))
    load_services(server)
    server.add_insecure_port(f'[::]:{config.PORT}')
    server.start()
    print(f"gRPC server running on port {config.PORT}") 
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down gRPC server...")
        server.stop(0)

if __name__ == '__main__':
    serve()