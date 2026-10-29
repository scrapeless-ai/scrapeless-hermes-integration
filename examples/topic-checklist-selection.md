# Documentation checklist

## Topic

Create and activate a Python virtual environment

Setup steps as stated on the page:

1. Create the environment with the `venv` module, pointing at a target directory (parents are created as needed):

```
python -m venv /path/to/new/virtual/environment
```

4. Activate it, POSIX shells:

```
source <venv>/bin/activate          # bash/zsh
source <venv>/bin/activate.fish     # fish
source <venv>/bin/activate.csh      # csh/tcsh
<venv>/bin/Activate.ps1             # pwsh
```

5. Activate it, Windows:

```
<venv>\Scripts\activate.bat         # cmd.exe
<venv>\Scripts\Activate.ps1         # PowerShell
```

6. Leave the environment — "You can deactivate a virtual environment by typing `deactivate` in your shell":

```
deactivate
```

## Source

https://docs.python.org/3.12/library/venv.html

Selected original setup steps 1, 4, 5 and 6 from the October 29 live output. Other steps, the checklist and notes remain in the full local output. These commands were generated as guidance and were not executed.
