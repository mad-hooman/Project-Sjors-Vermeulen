from bs4 import BeautifulSoup # type: ignore

def extract_monthly_listeners(html_string):
    """Extracts the monthly listeners count from an HTML string."""
    soup = BeautifulSoup(html_string, 'html.parser')
    listener_element = soup.find('div', {'data-testid': 'monthly-listeners-label'})

    if listener_element:
        text = listener_element.text
        listeners = ''.join(filter(str.isdigit, text))
        return listeners
    else:
        return None

def extract_monthly_listeners_from_file(filepath):
    """Extracts monthly listeners from a local HTML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return extract_monthly_listeners(html_content)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return None
    except Exception as e:
        print(f"An error occured: {e}")
        return None

# Replace 'artist_page.html' with the actual path to your saved file
filepath = './Spotify-Artist/artist.html' # or where ever you saved the file.

monthly_listeners = extract_monthly_listeners_from_file(filepath)

if monthly_listeners:
    print(f"Monthly listeners: {monthly_listeners}")
else:
    print("Monthly listeners count not found.")