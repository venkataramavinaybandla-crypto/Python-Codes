import subprocess

print("Network Scanner starting...\n")

subnet = input("Enter your subnet(example: 192.168.1. or 192.168.29.): ").strip()

print("Scanning...This may take some time!\n")
active_hosts = 0
inactive_hosts = 0

active_list = []
inactive_list = []

for i in range(1,256):
    ip = subnet + str(i)

    result = subprocess.run(["ping", "-n", "1", "-w", "300", ip],
                        stdout= subprocess.DEVNULL,
                        stderr=subprocess.PIPE
    )
    if result.returncode == 0:
        print(ip , " is Active")
        active_hosts += 1
        active_list.append(ip)
    else:
        inactive_list.append(ip)
        inactive_hosts += 1

print("Active Hosts: " + active_hosts)
print("Inactive Hosts: " + inactive_hosts)

print("Scanning Complete!\n")


