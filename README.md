# Newspaper Seller Simulation Case Study

## Description

This repository contains a case study project for the "Modeling & Simulation" subject. The primary objective is to determine the optimal number of newspapers a seller should purchase each day to maximize profits, considering daily demands classified as Good, Fair, or Poor days. The project includes a C++ console application for core simulations, a Python desktop GUI for user interaction, and comprehensive documentation in multiple formats.

### Problem Overview

- **Objective**: Maximize daily profit by determining the quantity of newspapers to purchase.
- **Parameters**:
  - Selling price per newspaper $(P)$: \$ $0.50$
  - Cost per newspaper $(C)$: \$ $0.33$
  - Scrap value per unsold newspaper $(S)$: \$ $0.05$
  - Daily demand $(d)$: Varies based on the type of day (Good, Fair, Poor)
  - Quantity of newspapers purchased $(X)$
- **Demand Distribution**: Possible demand values are $40, 50, 60, 70, 80, 90, 100$ newspapers, with probabilities depending on the day type.

### Model Formulation

The model calculates daily profit based on the following equations:

- Revenue from sales: $(\min(d, X) \times P)$
- Excess demand: $\max(X, d) - d$ (Note: This represents unsold newspapers, not excess demand in the standard sense)
- Profit per newspaper: $P - C$
- Lost profit: $\text{excess demand} \times (P - C)$
- Number of scraps: $\max(X, d) - d$ (Same as excess demand)
- Salvage from scraps: $\text{Number of scraps} \times S$
- Cost of daily newspapers: $X \times C$
- Daily Profit: $\text{Revenue Sales} - \text{Cost of daily newspapers} - \text{lost Profit} + \text{Salvage from scrap}$

**Note**: The definition of "excess demand" and "lost profit" differs from the standard newsvendor model, where lost profit typically relates to unmet demand $\max(d - X, 0) $. In this model, "excess demand" refers to unsold newspapers $\max(X - d, 0)$, leading to a unique profit calculation: $(P - C) \times \min(d, X) + (S - P) \times \max(X - d, 0)$.

## Project Structure

The repository is organized as follows:

| Folder/File | Description |
|-------------|-------------|
| `Console App/` | Core C++ implementation |
| &nbsp;&nbsp;&nbsp;&nbsp;`main.cpp` | Entry point for the console application simulating the newspaper seller’s decision-making |
| `Desktop-App/` | Python desktop GUI application |
| &nbsp;&nbsp;&nbsp;&nbsp;`main.py` | Entry point for the GUI application |
| &nbsp;&nbsp;&nbsp;&nbsp;`assets/` | Folder with GUI assets (e.g., images, icons) |
| &nbsp;&nbsp;&nbsp;&nbsp;`requirements.txt` | List of Python dependencies for the GUI |
| `Docs/` | Documentation and modeling files |
| &nbsp;&nbsp;&nbsp;&nbsp;`Newspaper Seller Case Study.docx` | Word document with detailed project information |
| &nbsp;&nbsp;&nbsp;&nbsp;`Newspaper Seller Case Study.pdf` | PDF version of the project documentation |
| &nbsp;&nbsp;&nbsp;&nbsp;`Newspaper Seller Problem - Modeling Simulation.xlsx` | Excel spreadsheet for modeling and simulation |
| HTML + CSS Documentation | A simple HTML + CSS documentation (e.g., `index.html`) available in the repository. Open with a web browser for interactive documentation |

## How to Run

### C++ Console Application

1. Ensure a C++ compiler is installed (e.g., [g++](https://gcc.gnu.org/) for Linux/Mac, [Visual Studio](https://visualstudio.microsoft.com/) for Windows).
2. Navigate to the `Console App/` directory.
3. Compile `main.cpp`:
   - For g++: `g++ main.cpp -o newspaper_simulation`
   - For Visual Studio: Open `main.cpp` in Visual Studio and build the project.
4. Run the executable:
   - Linux/Mac: `./newspaper_simulation`
   - Windows: `newspaper_simulation.exe`

### Python Desktop GUI

1. Ensure [Python](https://www.python.org/) is installed (check `requirements.txt` for the required version).
2. Navigate to the `Desktop-App/` directory.
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python main.py`

## Documentation

Detailed information about the project, including the problem definition, assumptions, and model formulation, is available in the `Docs/` folder:

- `Newspaper Seller Case Study.docx`: Comprehensive project details in Word format.
- `Newspaper Seller Case Study.pdf`: PDF version for easy sharing and viewing.
- `Newspaper Seller Problem - Modeling Simulation.xlsx`: Excel spreadsheet containing simulation data and modeling.

Additionally, an [online documentation](https://3bbaas.github.io/Newspaper-Selle-rSimulation-Case-Study/) is included in the repository. Locate the `index.html` file (or similar) and open it in a web browser for an interactive overview.

## Team Members:
- [Ahmed Abbas (Me)](https://github.com/3bbaas)
- [Rokiya Abdelsattar](https://github.com/RokiyaAbdElsatar)
- [Ahmed Ibrahim](https://github.com/jamika78)


<center>
  <br/>
  
  <p>That's all.</p>

</center>
