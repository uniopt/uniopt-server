import os
import sysconfig

platform = sysconfig.get_platform()
# curl command which contacts github api to get the release response about E+,
# will be processed in find_url_asset() and find_link()
curl_c = 'curl "https://api.github.com/repos/NREL/EnergyPlus/releases/latest"'
# getting the current directory for the downloaded file installation and turning window path
# to unix path ( \ -> / )
current_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/') + '/'

exe_dir = ''

file_name = ''


def find_url_asset():
    if "win" in platform:
        return 'findstr "browser_download_url"'
    else:
        return "grep browser_download_url"


def find_link():
    if "win-amd64" == platform:
        return 'findstr "Windows-x86_64.exe"'
    elif "win32" == platform:
        return 'findstr "Windows-i386.exe"'
    elif "linux-x86_64" == platform:
        return 'grep "[.]sh"'
    elif "macos" in  platform:
        return 'grep "Darwin-x86_64[.]dmg"'


def get_link():
    if "win" in platform:
        return find_link()
    else:
        return "cut -d '\"' -f 4"


def construct_link_c():
    command = curl_c + ' | ' + find_url_asset() + ' | ' + find_link() + ' | ' + get_link()
    return command


def run_link_c(command):
    os.system(command + " > tmp")
    output = open('tmp', 'r').read()
    os.remove("tmp")
    if "win" in platform:
        output = output.split('\"')
        output = output[3]
    return output


def download(link):
    global file_name
    file_name = link.split('/')[-1]
    command = "curl -fLO %s " % link
    os.system(command)


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
    get_home = "cd ~ | echo $PWD"
    os.system(get_home + " > tmp")
    get_home = open('tmp', 'r').read()
    os.remove("tmp")

    install_dir = "%a/EnergyPlus" % get_home
    mkdir = "mkdir %a" % install_dir
    os.system(mkdir)
    exe_dir = install_dir + file_name

    run = "echo -e \"y\n%s\" | ./%s" % (install_dir, exe_dir)
    os.system(run)


def silent_mac_install():
    # TODO
    return ''


def install_path():
    return exe_dir


def main():
    command = construct_link_c()
    link = run_link_c(command)
    download(link)
    install()
    return install_path()


if __name__ == "__main__":
    main()
