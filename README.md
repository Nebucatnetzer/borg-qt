# Borg-Qt

Borg-Qt is a Python 3 based graphical frontend for the backup tool
[BorgBackup](https://github.com/borgbackup/borg) as its name implies it is
using the Qt5 Framework. Currently it works only on Linux.


## Motivation

I think Borg is a great backup tool which should be available to many more
users. Since command line tools can be a bit scary for less experienced users I
decided to write a GUI as my "thesis" during my final semester at
the IBZ school in Aarau, Switzerland.

## Getting Started

These instructions will get you a copy of the project up and running on your
local machine.

### Prerequisites

You need to have Borg installed in order to have Borg-Qt working. You can get a
binary for your operating system here:
<https://github.com/borgbackup/borg/releases>

On a Debian based system you can install it by copying to `~/.local/bin/`. Borg
needs to be able to get executed by calling the command `borg`.

    cp ~/Downloads/borg-linux64 ~/.local/bin/borg
    chmod +x ~/.local/bin/borg

For other systems check their [documenation](https://borgbackup.readthedocs.io/en/stable/).

### Installing

Installing Borg-Qt is very simple. Download the binary for your operating
system here: <https://github.com/borgqt/borg-qt/releases>

You can then either run it by double clicking on it or by copying it to
`~/.local/bin/` like Borg. If you do that you might want to create a desktop
file for it. Puth the following code into a `borg-qt.desktop` file in
`~/.local/share/applications/`.

```
[Desktop Entry]
Version=1.0
Name=Borg-Qt
Exec=/home/username/.local/bin/borg-qt
Terminal=false
Type=Application
Categories=Tools
MimeType=x-scheme-handler/tg;
```

Make sure the file is executable:

``` shell
chmod +x ~/.local/share/applications/borg-qt.desktop
```

Now you should find Borg-Qt in your desktop's start menu.

## Development

To start working on Borg-Qt first clone the git repository and install
BorgBackup as described in [1.2.1].

    git clone https://github.com/borg-qt/borg-qt.git

Now create a virtual environment.

    cd borg-qt
    python3 -m venv venv

And activate it.

    source venv/bin/activate

Finally you can install the depencies.

    pip3 install -r requirements.txt

You're now all set to work on Borg-Qt. It's a good idea to run the tests before
starting. You can do this with the following command from the root of the
repository.

    make test

To make testing the application while programming a bit easier there's a script
which reloads the application everytime a file changes in the `borg_qt`
directory. You to use it run the following command from the root of the
repository.

    ./scripts/debugging.sh

### ToDos

To have a look at all the planned tasks you can have a look at the planned
features here: [todos.org](docs/todos.md)

## Used packages

-   [PyQt5](https://pyqt.readthedocs.io/en/latest/) - the GUI framework
-   [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/) - used for creating the binary

## Contributing

Everyone is welcome to submit pull requests and reports issues.
Please follow PEP8 and remove unnecessary white space when you contribute code.
And most importantly make sure that you don't break any tests and if possible
write tests for your code.

## Versioning

Currently there is no versioning as such. In the future a versioning scheme
based on [semantic versioning](http://semver.org/) might get used. The master
branch is considered to be the stable branch. Other branches might be highly
experimental.

## Authors

-   Andreas Zweili - *Initial work* - [Nebucatnetzer](https://github.com/Nebucatnetzer)

## License

This project is licensed under the GPLv3 License - see the <LICENSE> file
for details.

## Acknowledgments

-   Thanks to PurpleBooth for her [README template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2).
-   Thanks to [Back in Time](https://github.com/bit-team/backintime) for the inspiration.
-   Thanks to [Feather Icons](https://github.com/feathericons/feather) for their great icon set.

