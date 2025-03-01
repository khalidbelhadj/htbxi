#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    # Create proto directory if it doesn't exist
    proto_dir = os.path.join(os.path.dirname(__file__), 'proto')
    os.makedirs(proto_dir, exist_ok=True)
    
    # Copy the proto file from the frontend to the backend
    frontend_proto_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'frontend', 'src', 'proto', 'rent_prediction.proto')
    backend_proto_path = os.path.join(proto_dir, 'rent_prediction.proto')
    
    if not os.path.exists(frontend_proto_path):
        print(f"Error: Proto file not found at {frontend_proto_path}")
        return 1
    
    # Copy the proto file
    with open(frontend_proto_path, 'r') as src, open(backend_proto_path, 'w') as dst:
        dst.write(src.read())
    
    print(f"Copied proto file from {frontend_proto_path} to {backend_proto_path}")
    
    # Generate Python code from the proto file
    try:
        subprocess.check_call([
            'python', '-m', 'grpc_tools.protoc',
            f'--proto_path={proto_dir}',
            f'--python_out={proto_dir}',
            f'--grpc_python_out={proto_dir}',
            os.path.join(proto_dir, 'rent_prediction.proto')
        ])
        print("Successfully generated Python gRPC code")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error generating Python gRPC code: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 