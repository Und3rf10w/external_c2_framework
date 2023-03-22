package uname

import (
	"externalc2/pkg/utils/logging"

	"golang.org/x/sys/windows/registry"
)

type OsVer {
	CurrentVersion string
	ProductName string
	CurrentMajorVersionNumber int
	CurrentMajorVersionNumber int
	CurrentBuild int
}

type PlatformInfo {
	OS string
	OsVer OsVer
	Hostname string
	Arch string
}

// Reads the windows registry to collection system version information
func getOsVer() string {
	log.SetPrefix(logging.GetLogPrefix())
	// Adapted from: https://stackoverflow.com/a/44376544
	version := new(OsVer)
    k, err = registry.OpenKey(registry.LocalMachine, `SOFTWARE\Microsoft\Windows NT\CurrentVersion`, registry.QUERY_VALUE)
	if err != nil{
		log.Println("Unable to open SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion: ", err)
		version.CurrentVersion = "Unknown"
	}
	defer k.Close()

	version.CurrentVersion, _, err := k.GetStringValue("CurrentVersion")
	if err != nil {
		log.Println("Unable to read SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\CurrentVersion: ", err)
		version.CurrentVersion = "Unknown"
	}
	
	version.ProductName, _, err := k.GetStringValue("ProductName")
	if err != nil {
		log.Println("Unable to read SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProductName: ", err)
		version.ProductName = "Unknown"
	}

	version.CurrentMajorVersionNumber, _, err := k.GetStringValue("CurrentMajorVersionNumber")
	if err != nil {
		log.Println("Unable to read SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\CurrentMajorVersionNumber: ", err)
		version.CurrentMajorVersionNumber = "Unknown"
	}

	version.CurrentMinorVersionNumber, _, err := k.GetStringValue("CurrentMinorVersionNumber")
	if err != nil {
		log.Println("Unable to read SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\CurrentMinorVersionNumber: ", err)
		version.CurrentMinorVersionNumber = "Unknown"
	}

	version.CurrentBuild, _, err := k.GetStringValue("CurrentBuild")
	if err != nil {
		log.Println("Unable to read SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\CurrentBuild: ", err)
		version.CurrentBuild = "Unknown"
	}
    return version
}

// Returns operating system version information
func GetUname() *PlatformInfo {
    uname := new(PlatformInfo)
	uname.OS = runtime.GOOS
	uname.Arch = runtime.GOARCH
	uname.OsVer = getOsVer()
	uname.Hostname, err = os.Hostname()
	if err != nil {
		log.Println("Unable to determine hostname")
		uname.Hostname = ""
	}
	return uname
}