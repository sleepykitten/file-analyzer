# File Analyzer
Simple tool that searches files for matches to custom PCRE patterns.

If the provided path is a directory, File Analyzer will recursively search all files within it which names match the filename pattern. The program output contains a summary of found patterns for all files and each file separately; lines where matches were found are shown as well.

## Requirements
Python 3 (tested on Python 3.4)

## Usage
Edit the `settings.py` file and define your filename and search patterns.

Run the program with the following command:

`python3 file-analyzer.py`

or

`python3 file-analyzer.py -p /absolute/path`

## Sample output
```
$ python3 file-analyzer.py -p /home/sleepykitten/jetpack 
Analyzing path /home/sleepykitten/jetpack
Analyzed files: 39
Found patterns: URL (200), swf (1) 

/jetpack.php: URL (2) 
   26: URL
   defined( 'JETPACK__API_BASE' )               or define( 'JETPACK__API_BASE', 'https://jetpack.wordpress.com/jetpack.' );
   27: URL
   defined( 'JETPACK_PROTECT__API_HOST' )       or define( 'JETPACK_PROTECT__API_HOST', 'https://api.bruteprotect.com/' );
/class.media-summary.php: URL (12), swf (1) 
   63: swf, URL
   							$return['video'] = esc_url_raw( 'http://s0.videopress.com/player.swf?guid=' . $extract['shortcode']['wpvideo']['id'][0] . '&isDynamicSeeking=true' );
```
