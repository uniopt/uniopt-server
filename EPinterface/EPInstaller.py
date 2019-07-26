import os
import sysconfig
import urllib.request

# checking the os and the architecture of the host
platform = sysconfig.get_platform()
# request to github api getting the release response about E+,
# will be processed in construct_links()
api_call = urllib.request.urlopen('https://api.github.com/repos/NREL/EnergyPlus/releases/latest')
# getting the current directory for the downloaded file installation and turning window path
# to unix path ( \ -> / )
current_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/') + '/'

exe_dir = ''

file_name = ''

links = {}


def construct_links():
    global links
    response = api_call.read().decode("utf-8")
    response = response.split(',')
    all_links = []
    for asset in response:
        if "browser_download_url" in asset:
            all_links.append(asset)
    for link in all_links:
        link = link.replace('"', '')
        link = link.replace('}', '')
        link = link.replace(']', '')
        link = link.split(':', 1)
        if ".dmg" in link[1]:
            links['macos'] = link[1]
        elif "Windows-x86_64.exe" in link[1]:
            links['win64'] = link[1]
        elif "Windows-i386.exe" in link[1]:
            links['win32'] = link[1]
        elif ".sh" in link[1]:
            links['linux'] = link[1]


def download():
    global file_name
    if "win-amd64" == platform:
        file_name = links['win64'].split('/')[-1]
        local_filename, headers = urllib.request.urlretrieve(links['win64'], current_dir+file_name)
    elif "win32" == platform:
        file_name = links['win32'].split('/')[-1]
        local_filename, headers = urllib.request.urlretrieve(links['win32'], current_dir+file_name)
    elif "linux-x86_64" == platform:
        file_name = links['linux'].split('/')[-1]
        # local_filename, headers = urllib.request.urlretrieve(links['linux'], current_dir+file_name)
    elif "macos" in  platform:
        file_name = links['macos'].split('/')[-1]
        local_filename, headers = urllib.request.urlretrieve(links['macos'], current_dir+file_name)


def install():
    if "win" in platform:
        return silent_win_install()
    elif "linux-x86_64" == platform:
        return silent_linux_install()
    elif "macos" in platform:
        return silent_mac_install()


def silent_win_install():
    """
    The function will use a windows feature for silent install
    choosing the default setting

    EnergyPlus will be installed in [C:/EnergyPlusVX-X-X]

    """
    global exe_dir
    exe_dir = current_dir + file_name
    command = "%s /S" % exe_dir
    return os.system(command)


def silent_linux_install():
    """
    In this function The approach is to get the home directory to
    install the program without root privilege. And since telda ~
    isn't accepted as an installation path we'll get the home directory
    and then pass it as argument to the interactive shell
    file using echo -e simulating user input

    EnergyPlus will be installed in [/home/$username$/EnergyPlus]
    """
    global exe_dir
    homedir = os.path.expanduser("~")

    install_dir = "%s/EnergyPlus" % homedir
    mkdir = "mkdir %s" % install_dir
    os.system(mkdir)
    exe_dir = current_dir + "Energy*.sh"
    run = "echo \"y\\n%s\" | ./%s" % (install_dir, file_name)
    os.system(run)


def silent_mac_install():
    # TODO
    return ''


def install_path():
    return exe_dir


def main():
    construct_links()
    download()
    install()


if __name__ == "__main__":
    main()
