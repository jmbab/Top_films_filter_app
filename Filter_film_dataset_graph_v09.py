# FILTERING THROUGH IMDB TOP 1000 FILMS
# READING FROM A BIG DATASET IN PYTHON
# INCLUSION OF GENERATORS TO SAVE MEMORY
# + MULTI-FILTERING RESULTS AND ERROR HANDLING
# MADE USER-FRIENDLY IN A SEARCH WINDOW 
# WITH APPLY, RESET BUTTONS, AND PAGINATION OF RESULTS
# AND CREATE GRAPH OF TREND EVOLUTION THROUGH TIME
# Jean M. Babonneau - 01-11-2024

import csv
import tkinter as tk
from tkinter import ttk, messagebox
from itertools import islice
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# Path to the CSV file
script_dir = Path(__file__).parent
csv_file_path = script_dir / 'imdb_top_1000_movies.csv'

# Generator to read movies from the CSV file line by line
def read_movies_from_csv():
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            required_columns = {'title', 'genres', 'averageRating', 'releaseYear'}
            if not required_columns.issubset(reader.fieldnames):
                raise KeyError("CSV file must contain columns: title, genres, averageRating, releaseYear")
            for row in reader:
                try:
                    row['averageRating'] = float(row['averageRating'])
                    row['releaseYear'] = int(row['releaseYear'])
                    yield row
                except ValueError:
                    continue  # Skip rows with invalid data
    except FileNotFoundError:
        messagebox.showerror("File Error", "The specified CSV file was not found.")
    except KeyError as e:
        messagebox.showerror("CSV Error", str(e))

# Load movies into a list for initial filtering and pagination
all_movies = list(read_movies_from_csv())
current_movies = all_movies  # This will hold the filtered movies
current_page = 1
movies_per_page = 20
sort_ascending = {'title': True, 'releaseYear': True, 'genres': True, 'averageRating': True}

# Initialize the main window
root = tk.Tk()
root.title("IMDb Top 1000 Movie Filter")
root.geometry("900x600")

# Pagination controls
def go_previous():
    global current_page
    if current_page > 1:
        current_page -= 1
        display_movies(page=current_page)

def go_next():
    global current_page
    total_pages = (len(current_movies) // movies_per_page) + (1 if len(current_movies) % movies_per_page > 0 else 0)
    if current_page < total_pages:
        current_page += 1
        display_movies(page=current_page)

# Function to display movies on the current page
def display_movies(page=1):
    table.delete(*table.get_children())  # Clear previous entries

    start_idx = (page - 1) * movies_per_page
    end_idx = start_idx + movies_per_page
    movies_to_display = islice(current_movies, start_idx, end_idx)

    for movie in movies_to_display:
        table.insert("", tk.END, values=(movie["title"], movie["releaseYear"], movie["genres"], f"{movie['averageRating']:.1f}"))

    total_pages = (len(current_movies) // movies_per_page) + (1 if len(current_movies) % movies_per_page > 0 else 0)
    page_label.config(text=f"Page {page} of {total_pages}")
    prev_button.config(state=tk.NORMAL if page > 1 else tk.DISABLED)
    next_button.config(state=tk.NORMAL if page < total_pages else tk.DISABLED)

# Sorting function for the Treeview columns
def sort_by_column(column):
    global current_movies, sort_ascending
    reverse = not sort_ascending[column]  # Toggle sort order
    current_movies.sort(key=lambda x: x[column] if x[column] else '', reverse=reverse)
    sort_ascending[column] = reverse  # Update sort order for next click
    display_movies(current_page)  # Refresh table

# Function to apply filters based on user input
def apply_filters():
    global current_movies, current_page

    # Get filter values
    keyword = search_entry.get().strip().lower()
    from_year = from_year_entry.get().strip()
    to_year = to_year_entry.get().strip()
    selected_genre = genre_combobox.get()
    min_rating = min_rating_entry.get().strip()

    # Start with all movies and apply filters using generator expressions
    filtered_movies = (movie for movie in all_movies)

    if keyword:
        filtered_movies = (movie for movie in filtered_movies if keyword in movie['title'].lower())

    if from_year.isdigit():
        from_year = int(from_year)
        filtered_movies = (movie for movie in filtered_movies if movie['releaseYear'] >= from_year)

    if to_year.isdigit():
        to_year = int(to_year)
        filtered_movies = (movie for movie in filtered_movies if movie['releaseYear'] <= to_year)

    if selected_genre:
        filtered_movies = (movie for movie in filtered_movies if selected_genre in movie['genres'].split(", "))

    if min_rating:
        try:
            min_rating = float(min_rating)
            filtered_movies = (movie for movie in filtered_movies if movie['averageRating'] >= min_rating)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for minimum rating.")
            return

    current_movies = list(filtered_movies)
    current_page = 1
    display_movies(page=current_page)

# Reset filters and show all movies
def reset_filters():
    global current_movies, current_page

    # Clear filter inputs
    search_entry.delete(0, tk.END)
    from_year_entry.delete(0, tk.END)
    to_year_entry.delete(0, tk.END)
    genre_combobox.set('')
    min_rating_entry.delete(0, tk.END)

    # Reset to the full list and display
    current_movies = all_movies
    current_page = 1
    display_movies(page=current_page)

# Function to generate the graph of average ratings per genre over the years based on the current filter
def show_genre_rating_trends():
    data = pd.DataFrame(current_movies)
    data['averageRating'] = pd.to_numeric(data['averageRating'], errors='coerce')
    data['releaseYear'] = pd.to_numeric(data['releaseYear'], errors='coerce')
    data.dropna(subset=['averageRating', 'releaseYear'], inplace=True)

    genre_year_ratings = []
    for _, row in data.iterrows():
        genres = row['genres'].split(", ")
        for genre in genres:
            genre_year_ratings.append({
                'genre': genre,
                'releaseYear': row['releaseYear'],
                'averageRating': row['averageRating']
            })

    genre_data = pd.DataFrame(genre_year_ratings)
    genre_trends = genre_data.groupby(['genre', 'releaseYear']).mean().reset_index()

    fig, ax = plt.subplots(figsize=(8, 5))  # Adjusted graph size for additional left space
    genre_lines = {}

    for genre in genre_trends['genre'].unique():
        genre_subset = genre_trends[genre_trends['genre'] == genre]
        line, = ax.plot(genre_subset['releaseYear'], genre_subset['averageRating'], label=genre)
        genre_lines[genre] = line
        line.set_visible(False)  # Start with all lines hidden

    def toggle_visibility(genre):
        line = genre_lines[genre]
        line.set_visible(not line.get_visible())
        plt.draw()

    def hide_all():
        for line in genre_lines.values():
            line.set_visible(False)
        plt.draw()

    plt.xlabel('Year')
    plt.ylabel('Average Rating')
    plt.title('Average Movie Ratings by Genre Over the Years')
    plt.grid(True)
    plt.tight_layout()

    # Create the genre list window and align it next to the graph window
    genre_list_window = tk.Toplevel(root)
    genre_list_window.title("Genre Rating Trends")
    genre_list_window.geometry("200x500+10+50")  # Adjust position as per main window position

    # Populate list with colored dots and genre names
    genre_list_frame = tk.Frame(genre_list_window)
    genre_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for genre, line in genre_lines.items():
        color = line.get_color()
        label = tk.Label(
            genre_list_frame,
            text=genre,
            font=("Helvetica", 10),
            anchor="w",
            padx=10,
            compound="left"
        )
        color_dot = tk.Canvas(label, width=10, height=10, bg=color, highlightthickness=0)
        color_dot.create_oval(2, 2, 10, 10, fill=color, outline=color)
        color_dot.pack(side="left")
        label.bind("<Button-1>", lambda e, g=genre: toggle_visibility(g))
        label.pack(fill="x", padx=5, pady=2)

    hide_all_button = tk.Button(genre_list_frame, text="Hide All", command=hide_all)
    hide_all_button.pack(pady=(10, 5))

    legend = ax.legend(title='Genre', bbox_to_anchor=(-0.35, 1), loc='upper left', borderaxespad=0.)

    plt.show()

# Main GUI setup

# Filter controls
filter_frame = tk.Frame(root)
filter_frame.pack(fill=tk.X, padx=10, pady=5)

tk.Label(filter_frame, text="Search Title:").pack(side=tk.LEFT, padx=(0, 5))
search_entry = tk.Entry(filter_frame)
search_entry.pack(side=tk.LEFT, padx=(0, 10))

tk.Label(filter_frame, text="From Year:").pack(side=tk.LEFT, padx=(0, 5))
from_year_entry = tk.Entry(filter_frame, width=5)
from_year_entry.pack(side=tk.LEFT)

tk.Label(filter_frame, text="To Year:").pack(side=tk.LEFT, padx=(10, 5))
to_year_entry = tk.Entry(filter_frame, width=5)
to_year_entry.pack(side=tk.LEFT)

tk.Label(filter_frame, text="Genre:").pack(side=tk.LEFT, padx=(10, 5))
unique_genres = sorted(set(genre.split(", ")[0] for movie in all_movies for genre in movie['genres'].split(", ")))
genre_combobox = ttk.Combobox(filter_frame, values=unique_genres, width=15, state="readonly")
genre_combobox.pack(side=tk.LEFT)

tk.Label(filter_frame, text="Min Rating:").pack(side=tk.LEFT, padx=(10, 5))
min_rating_entry = tk.Entry(filter_frame, width=5)
min_rating_entry.pack(side=tk.LEFT)

apply_button = tk.Button(filter_frame, text="Apply", command=apply_filters)
apply_button.pack(side=tk.LEFT, padx=(10, 5))
reset_button = tk.Button(filter_frame, text="Reset", command=reset_filters)
reset_button.pack(side=tk.LEFT, padx=(5, 0))

# Pagination and graph button
pagination_frame = tk.Frame(root)
pagination_frame.pack(fill=tk.X, padx=10, pady=5)

prev_button = tk.Button(pagination_frame, text="Previous", command=go_previous)
prev_button.pack(side=tk.LEFT, padx=(10, 5))
page_label = tk.Label(pagination_frame, text="Page 1 of 1")
page_label.pack(side=tk.LEFT)
next_button = tk.Button(pagination_frame, text="Next", command=go_next)
next_button.pack(side=tk.LEFT, padx=(5, 10))

show_graph_button = tk.Button(pagination_frame, text="Show Genre Rating Trends", command=show_genre_rating_trends)
show_graph_button.pack(side=tk.RIGHT)

# Display the table
table_frame = tk.Frame(root)
table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

style = ttk.Style()
style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="lightgray")

table = ttk.Treeview(table_frame, columns=("Title", "Year", "Genres", "Rating"), show="headings", height=20)
table.heading("Title", text="Title", command=lambda: sort_by_column("title"))
table.heading("Year", text="Year", command=lambda: sort_by_column("releaseYear"))
table.heading("Genres", text="Genres", command=lambda: sort_by_column("genres"))
table.heading("Rating", text="Rating", command=lambda: sort_by_column("averageRating"))

table.column("Title", anchor=tk.W, width=300)
table.column("Year", anchor=tk.CENTER, width=80)
table.column("Genres", anchor=tk.W, width=200)
table.column("Rating", anchor=tk.CENTER, width=80)

table.pack(fill=tk.BOTH, expand=True)

# Initial display of movies
display_movies(page=current_page)

# Start the Tkinter main loop
root.mainloop()

