# Zillow Property Search

## Introduction
The Zillow Property Search is a Streamlit web application designed to facilitate the search for real estate properties listed on Zillow. This application provides users with a simple interface to input a city name and retrieve property listings available in that city from the Zillow website.

## Features
- **City-Based Property Search**: Users can input the name of a city to search for property listings.
- **Retrieval of Property Listings**: The application retrieves property listings from Zillow's website based on the specified city.
- **User-Friendly Interface**: The user interface is intuitive and easy to use, with minimalistic design elements.

## Prerequisites
Before running the Zillow Property Search application, activate a virtual environment. 
# Python virtual environments using venv

Virtual environments are a useful way of separating dependencies and establishing a working environment for Python projects. The most common way of achieving this is through the use of `virtualenv` or `pipenv`. But since Python 3.3, a subset of `virtualenv` has been integrated into the standard library under the `venv` [module](https://docs.python.org/3/library/venv.html). Though not as featureful as the former two, `venv` is a simple way of getting a functional virtual environment setup.

This gist was inspired by Corey Schafer's [video](https://www.youtube.com/watch?v=Kg1Yvry_Ydk) on `venv`.

The commands are intended to be used on any Arch-based Linux distribution. For others distros, `python3` and `pip3` might be the way to go.

## Using venv

Since `venv` is a built-in module of any stock Python installation we don't need to install anything (apart from `python-pip` if it's not yet installed).

To create a virtual environment in the _virtual_env_ folder:

```
python -m venv virtual_env
```

In order for the virtual environment to have access to globally installed Python packages the flag `--system-site-packages` should be used.

To activate the virtual environment
```
source virtual_env/bin/activate
```
This will add some text to your command prompt indicating that the environment is activated. The output of ```pip list``` should be different than the one we see without the virtual environment.

Typing ```which python``` will retrieve the path of the Python interpreter which the venv will use. The version of Python used in the virtual environment will be the same as the one that was installed in the system when the venv was created. If you REALLY need to use different Python versions you must use other solutions, like `virtualenv`.

To deactivate the virtual environment just type
```
deactivate
```

## Installing packages

Packages can be installed with ```pip```. These will exist only within the virtual environment and will not be accesible otherwise.

```
pip install package_name
```

## Export package list

We can generate a list of required packages so anybody can create an environment which uses the same requirements and dependencies (and the same versions).

```
pip freeze > requirements.txt
```

If the venv has access to globally installed packages and we only want to add locally installed packages to requirements.txt add the `--local` flag.

With the virtual environment activated we can install the packages in the requirements.txt file:

```
pip install -r requirements.txt
```

## Other options

Then ensure you have the following dependencies installed:

- Python 3.x
- Streamlit
- BeautifulSoup
- requests
- xmltodict

Install these dependencies using pip:
```
pip install streamlit beautifulsoup4 requests xmltodict
```

## How to Run
Follow these steps to run the Zillow Property Search application:

1. **Clone the Repository**: Clone this repository to your local machine using Git.
   ```
   git clone https://github.com/yourusername/zillow-property-search.git
   ```

2. **Navigate to the Directory**: Open a terminal or command prompt and navigate to the directory where the code is located.
   ```
   cd zillow-property-search
   ```

3. **Run the Streamlit App**: Execute the Streamlit app using the following command:
   ```
   streamlit run zillow_property_search.py
   ```

4. **Access the Application**: Once the Streamlit server starts, it will provide a URL that you can open in your web browser. Open the provided URL to access the Zillow Property Search application.

5. **Perform Property Search**: Enter the name of the city you want to search for properties in the input field and click the "Search" button.

6. **View Search Results**: The application will display the search results, including property details such as price, address, and additional information.

## Contributing
Contributions to the Zillow Property Search application are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request on the GitHub repository.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- The Zillow Property Search application was inspired by the need for a simple and efficient tool to search for real estate properties on Zillow.
- Special thanks to the Streamlit and BeautifulSoup communities for their excellent tools and documentation.
