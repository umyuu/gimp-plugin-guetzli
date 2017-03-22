# gimp-plugins [GitHub](https://github.com/umyuu/gimp-plugins)

3rd Party
gimp-plugins Guetzli executable file call wrapper. 

## Install
1. [download a ZIP](https://github.com/umyuu/gimp-plugins/archive/master.zip) file.
2. setup

  - [ ]  zip extract plug-ins Directory copy to GIMP plug-ins Directory.
  - [ ]  [Guetzli executable file](https://github.com/google/guetzli/releases) copy to GIMP plug-ins Directory.


[FYI:setup.txt](docs/setup.txt)

## Plugin Run.
1. Run GIMP

2. Open jpg/png Image File

3. File Menu -> Export -> Save guetzli

   ![Save guetzli](docs/dialog.png)
   
   Save .jpeg file

4. Open .jpeg file

## Plugin Specification
When multiple files are opened, the file on the rightmost side is processed

## Uninstall
Delete the file copied to GIMP plug-ins Directory.
