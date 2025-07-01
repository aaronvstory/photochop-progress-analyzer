# Setup Guide

This guide will help you get Photochop Progress Analyzer up and running on your system.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.7 or higher
- **RAM**: 512MB available memory
- **Storage**: 50MB free disk space
- **Permissions**: Administrator access on Windows for batch file launcher

### Recommended Requirements
- **Python**: Version 3.9 or higher
- **RAM**: 2GB available memory (for better performance with large folder structures)
- **CPU**: Multi-core processor for faster folder scanning

## Installation Steps

### Step 1: Install Python

#### Windows
1. Download Python from [python.org/downloads](https://python.org/downloads)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   ```

#### macOS
```bash
# Using Homebrew (recommended)
brew install python

# Or download from python.org
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Step 2: Download Photochop Progress Analyzer

#### Option A: Download Release (Recommended)
1. Go to [GitHub Releases](https://github.com/aaronvstory/photochop-progress-analyzer/releases)
2. Download the latest release ZIP file
3. Extract to your preferred location (e.g., `C:\Tools\photochop-analyzer\`)

#### Option B: Clone Repository
```bash
git clone https://github.com/aaronvstory/photochop-progress-analyzer.git
cd photochop-progress-analyzer
```

### Step 3: Install Dependencies

Open terminal/command prompt in the project directory and run:

```bash
pip install psutil
```

#### Troubleshooting Dependency Installation

**Permission Issues (Linux/macOS)**:
```bash
pip install --user psutil
```

**Python 2/3 Conflicts**:
```bash
pip3 install psutil
python3 -m pip install psutil
```

**Corporate Networks/Proxies**:
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org psutil
```

### Step 4: Verify Installation

Navigate to the `src/` directory and test:

#### Windows
```cmd
cd src
python photoshop_monitor.py --help
```

#### macOS/Linux
```bash
cd src/
python3 photoshop_monitor.py --help
```

You should see the help message with available command options.

## First Run

### Windows Users (Recommended Method)
1. Navigate to the `src/` folder
2. **Right-click** on `run_photoshop_monitor.bat`
3. Select **"Run as Administrator"**
4. Follow the interactive menu

### All Platforms (Command Line)
```bash
cd src/
python photoshop_monitor.py --select-folder
```

This will open a folder picker to select your monitoring directory.

## Configuration

### Default Configuration
The application creates `monitor_config.json` with default settings:

```json
{
  "base_path": "C:\\Users\\%USERNAME%\\Downloads",
  "last_update": null
}
```

### Custom Configuration
You can edit this file before first run to set your preferred default path:

```json
{
  "base_path": "C:\\Your\\Custom\\Path",
  "last_update": null
}
```

## Folder Structure Requirements

For the analyzer to work correctly, your folder structure should look like:

```
Your Monitor Folder/
├── project1/
│   ├── subfolder1/
│   │   ├── image1.jpg
│   │   └── gen-image1_expanded.jpg
│   └── subfolder2/
│       └── image2.jpg
└── project2/
    └── user_001/
        ├── photo.jpg
        └── gen-photo_expanded.jpg
```

### Key Points:
- Monitor folder contains subfolders (projects)
- Each subfolder can contain image files
- Files starting with `gen-` are considered "processed"
- Supports `.jpg`, `.jpeg`, `.png`, `.webp` image formats

## Testing Your Setup

### Quick Test
1. Create a test folder structure:
   ```
   test_monitor/
   ├── folder1/
   │   ├── test1.jpg
   │   └── gen-test1_expanded.jpg
   └── folder2/
       └── test2.jpg
   ```

2. Run the analyzer:
   ```bash
   python photoshop_monitor.py --path "path/to/test_monitor"
   ```

3. Expected output:
   - Total folders: 2
   - Processed: 1 (folder1)
   - Pending: 1 (folder2)

## Troubleshooting

### Common Issues

#### "Python not found"
- Ensure Python is installed and added to PATH
- Try `python3` instead of `python`
- Restart terminal/command prompt after Python installation

#### "Permission denied" (Windows)
- Run batch file as Administrator
- Or run Command Prompt as Administrator

#### "No module named 'psutil'"
```bash
pip install psutil
# or
pip3 install psutil
```

#### "No data found"
- Verify the folder contains subfolders
- Check that subfolders contain image files
- Ensure you have read permissions for the directory

#### Performance Issues
- For folders with 1000+ subfolders, initial scan may take 10-30 seconds
- Close unnecessary applications to free up system resources
- Consider monitoring smaller folder sections

### Getting Help

1. **Check the logs**: Look for error messages in the console output
2. **Verify folder structure**: Ensure your folders match the expected format
3. **Test with a simple folder**: Create a minimal test case
4. **Check permissions**: Ensure you can read the target folders
5. **Update dependencies**: Run `pip install --upgrade psutil`

## Advanced Configuration

### Environment Variables
You can set environment variables to customize behavior:

```bash
# Windows
set PYTHONPATH=%PYTHONPATH%;C:\path\to\photochop-analyzer\src

# Linux/macOS
export PYTHONPATH=$PYTHONPATH:/path/to/photochop-analyzer/src
```

### Running as Service (Advanced)
For continuous monitoring, you can set up the analyzer as a system service:

#### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., at startup)
4. Set action to run the batch file with admin privileges

#### Linux (systemd)
Create a service file in `/etc/systemd/system/photochop-monitor.service`

## Next Steps

After successful installation:

1. **Familiarize yourself** with the interactive menu system
2. **Test different monitoring modes** (single check vs. continuous)
3. **Explore the performance analytics** features
4. **Set up your actual Photoshop project folders** for monitoring
5. **Consider automation** for your workflow needs

## Support

If you encounter issues not covered in this guide:

- Check [GitHub Issues](https://github.com/aaronvstory/photochop-progress-analyzer/issues)
- Create a new issue with detailed error information
- Include your operating system, Python version, and error messages
