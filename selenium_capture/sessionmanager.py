import subprocess

# control all sessions
class sessionManager():
    def __init__(self):
        self.shared_memory_pool = {} 
        
    def setup_docker(self,user_id):
        result = subprocess.run("pwd", shell=True, capture_output=True, text=True)
        output = result.stdout.strip()
        print("Current Directory:", output)

    def terminate(self,user_id,all = None):
        if all:
            for item in self.shared_memory_pool.items():
                item.close()
                item.unlink()
        self.shared_memory_pool[f'sms_{user_id}'].close()
        self.shared_memory_pool[f'sms_{user_id}'].unlink()