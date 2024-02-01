# Zillow Property Search

## Introduction
The Zillow Property Search is a Streamlit web application designed to facilitate the search for real estate properties listed on Zillow. This application provides users with a simple interface to input a city name and retrieve property listings available in that city from the Zillow website.

## Features
- **City-Based Property Search**: Users can input the name of a city to search for property listings.
- **Retrieval of Property Listings**: The application retrieves property listings from Zillow's website based on the specified city.
- **User-Friendly Interface**: The user interface is intuitive and easy to use, with minimalistic design elements.

## Prerequisites
Before running the Zillow Property Search application, ensure you have the following dependencies installed:

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
