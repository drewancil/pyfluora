# Installing pyfluora in Other Projects

## Quick Start

### Option 1: Direct Installation (Recommended)
```bash
# Navigate to your other project
cd /path/to/your/other/project

# Activate that project's virtual environment
source venv/bin/activate  # or however you activate it

# Install pyfluora from local source
pip install /Users/andrew/Development/pyfluora
```

### Option 2: Editable Installation (For Development)
```bash
# Same setup as above, then:
pip install -e /Users/andrew/Development/pyfluora

# Now any changes you make to pyfluora source code
# will be immediately available in your other project
```

### Option 3: Install from Built Wheel
```bash
# Install the pre-built package
pip install /Users/andrew/Development/pyfluora/dist/pyfluora-0.0.4-py3-none-any.whl
```

## Complete Example Setup

Let's say you have another project at `/Users/andrew/my-plant-controller`:

```bash
# 1. Navigate to your other project
cd /Users/andrew/my-plant-controller

# 2. Create/activate virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install pyfluora (choose one method)
pip install -e /Users/andrew/Development/pyfluora  # Editable install

# 4. Verify installation
python -c "import fluoraapi; print('✅ pyfluora installed successfully!')"

# 5. Now you can use it in your project
```

## Using in Your Other Project

Create a file like `my-plant-controller/main.py`:

```python
#!/usr/bin/env python3
"""Example usage of pyfluora in another project."""

from fluoraapi import FluoraAPI
import time

def main():
    # Use your pyfluora package
    with FluoraAPI("192.168.1.100", 4210, "0.0.0.0", 12345) as api:
        print("Connected to Fluora plant!")
        
        api.power(1)
        api.brightness_set(0.7)
        api.animation_set_manual("RAINBOW")
        
        time.sleep(5)
        
        state = api.plant_state
        if state:
            print(f"Current brightness: {state.brightness}")
        
    print("Done!")

if __name__ == "__main__":
    main()
```

## Requirements File Method

You can also add it to your other project's `requirements.txt`:

```txt
# requirements.txt in your other project

# Install pyfluora from local path
pyfluora @ file:///Users/andrew/Development/pyfluora

# Or for editable install
# -e /Users/andrew/Development/pyfluora

# Other dependencies...
requests>=2.25.0
```

Then install with:
```bash
pip install -r requirements.txt
```

## Dependency Management

### Method 1: Direct Dependencies
If your other project's `requirements.txt` or `pyproject.toml` lists the pyfluora dependencies:

```txt
# Your other project's requirements.txt
pyfluora @ file:///Users/andrew/Development/pyfluora
python-osc>=1.8.0
python-box>=7.0.0
```

### Method 2: Let pyfluora Handle Dependencies (Recommended)
Just install pyfluora and let it handle its own dependencies:

```bash
pip install -e /Users/andrew/Development/pyfluora
# This automatically installs python-osc and python-box
```

## Troubleshooting

### Import Issues
If you get `ModuleNotFoundError`:

```bash
# Check if installed
pip list | grep pyfluora

# Check install location
pip show pyfluora

# Try reimporting
python -c "import sys; print(sys.path)"
python -c "import fluoraapi; print(fluoraapi.__file__)"
```

### Version Conflicts
If you need a specific version:

```bash
# Uninstall first
pip uninstall pyfluora

# Reinstall
pip install -e /Users/andrew/Development/pyfluora
```

### Multiple Projects
For multiple projects using different versions:

```bash
# Project A (uses latest development version)
cd /path/to/project-a
source venv/bin/activate
pip install -e /Users/andrew/Development/pyfluora

# Project B (uses specific wheel version)
cd /path/to/project-b  
source venv/bin/activate
pip install /Users/andrew/Development/pyfluora/dist/pyfluora-0.0.4-py3-none-any.whl
```

## Best Practices

1. **Use editable installs** (`-e`) during development for immediate updates
2. **Use wheel installs** for production or when you want a stable version
3. **Always use virtual environments** to avoid conflicts
4. **Pin versions** in requirements.txt for reproducible builds
5. **Test imports** after installation to verify everything works

## Next Steps

Once you're ready to distribute:
1. Push to GitHub
2. Create releases/tags
3. Publish to PyPI
4. Then other projects can install with: `pip install pyfluora`