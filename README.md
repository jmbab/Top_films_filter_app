# IMDb Top 1000 Movie Filter

This project is a Python-based GUI application that filters and paginates the top 1000 IMDb movies based on various criteria.
It uses Python generators to spare memory usage.

## Requirements

- Python 3.x (no additional packages required)

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jmbab/Top_films_filter_app.git
   cd Top_films_filter_app

2. **Create a virtual environment (optional but recommended to isolate dependencies)**:

   ```bash
   python -m venv venv

3. **Activate the virtual environment**:

- On Windows:

   ```bash
   venv\Scripts\activate

- On macOS/Linux:

   ```bash
   source venv/bin/activate

4. **Run the script**:

   ```bash
   python your_script_name.py

## Usage

The application provides an intuitive GUI for filtering the top 1000 movies on IMDb.com based on the following criteria:

- by Title: Search for keywords among the Top 1000 IMDb movie titles.
- by Year Range: Filter movies from a specified starting year to an ending year.
- by Genre: Filter by genre using a dropdown menu of main genres.
- by Minimum Rating: Filter by minimum IMDb rating.

Use the pagination controls to navigate through the results, which display 20 movies per page.

## Notes

Ensure that the imdb_top_1000_movies.csv file is placed in the specified path within the script or in the same directory as the script.
The .gitignore file should exclude temporary files, such as venv/, to avoid committing unnecessary files to version control.

## License

This project is open-source and available under the MIT License.

For further details, visit the repository on GitHub: https://github.com/jmbab/Top_films_filter_app
