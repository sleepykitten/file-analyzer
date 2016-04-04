#!/usr/bin/env python

# File Analyzer: Simple tool that searches files for matches to custom PCRE patterns.
# Copyright (C) 2016 sleepykitten
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import argparse
import os
import re
import sys
from collections import OrderedDict

class FileAnalyzer( object ):
	def __init__( self ):
		self.init()
		self.analyze_files()
		self.show_results()

	def init( self ):
		self.get_settings()
		self.analyzed_files = 0
		self.results_output = ""
		self.results_found_patterns = {}

	def get_settings( self ):
		"""Loads settings from settings.py"""
		settings_file_path = os.path.dirname( os.path.realpath( __file__ ) ) + "/settings.py"
		settings_file_exists = os.path.isfile( settings_file_path )

		if not settings_file_exists:
			print( "Error: Settings file does not exist." )
			sys.exit()

		settings = {}
		exec( open( settings_file_path ).read(), settings )
		self.path = settings["path"].strip()
		self.filename_pattern = settings["filename_pattern"].strip()
		self.search_patterns = settings["search_patterns"]

		if not self.filename_pattern:
			print( "Error: No filename pattern specified." )
			sys.exit()
		if len( self.search_patterns ) == 0:
			print( "Error: No regex patterns specified." )
			sys.exit()

	def analyze_files( self ):
		"""Recursively analyzes files according to settings"""
		parser = argparse.ArgumentParser( description = "Simple tool that searches files for matches to custom PCRE patterns." )
		parser.add_argument( "-p", "--path", help = "Absolute file/directory path that should be analyzed", required = False )
		arguments = vars( parser.parse_args() )

		# Checks whether the path is provided as an argument
		if arguments[ "path" ]:
			provided_path = arguments[ "path" ]
		else:
			if self.path:
				provided_path = self.path
				print( "No path argument provided, using path from settings.py." )
			else:
				provided_path = input( "Absolute file/directory path that should be analyzed: " )

		provided_path_exists = os.path.exists( provided_path )
		if provided_path_exists == True:
			self.provided_path = provided_path
		else:
			print( "Error: Invalid path provided." )
			sys.exit()

		print( "Analyzing path %s" % self.provided_path )

		if os.path.isdir( self.provided_path ):
			for dirpath, dirnames, files in os.walk( self.provided_path ):
					for name in files:
						if not re.search( self.filename_pattern, name ):
							continue
						self.analyze_file( os.path.join( dirpath, name ) )
		else:
			if re.search( self.filename_pattern, self.provided_path ):
				self.analyze_file( self.provided_path )

	def analyze_file( self, file_path ):
		"""Analyzes a single file"""
		file_handle = open( file_path, "r", encoding = "utf-8", errors = "ignore" )
		file_found_patterns = {}
		file_results = {}
		line_number = 1

		# Creates a dictionary with lines and found patterns 
		for line_contents in file_handle.readlines():
			for item in self.search_patterns:
				matches = re.findall( item, line_contents )
				matches_count = len( matches )
				if matches_count > 0:
					if not self.search_patterns[ item ].strip():
						pattern_name = "Unnamed pattern"
					else:
						pattern_name = self.search_patterns[ item ]

					file_found_patterns[ pattern_name ] = self.get_file_found_patterns( file_found_patterns, pattern_name, matches_count )

					if not line_number in file_results:
						file_results[ line_number ] = { "patterns" : { pattern_name : matches }, "line" : line_contents }
					else:
						file_results[ line_number ][ "patterns" ][ pattern_name ] = matches
			line_number += 1
		file_handle.close()
		file_results = self.get_dictionary_sorted_by_key( file_results )
		self.aggregate_results( file_path, file_found_patterns, file_results )
		self.analyzed_files += 1

	def aggregate_results( self, file_path, file_found_patterns, file_results ):
		"""Aggregates results"""
		if len( file_found_patterns ) == 0:
			return
		else:
			# Aggregates found patterns
			self.results_found_patterns = { x: self.results_found_patterns.get( x, 0 ) + file_found_patterns.get( x, 0 ) for x in set( self.results_found_patterns ).union( file_found_patterns ) } # Combines dictionaries
			file_found_patterns_string = self.get_string_from_dict( self.get_dictionary_sorted_by_key( file_found_patterns ) )

		# Removes part of the path
		file_path_shortened = file_path.replace( self.provided_path, "")
		if not file_path_shortened:
			file_path_shortened = file_path

		self.results_output += "%s: %s \n" % ( file_path_shortened, file_found_patterns_string )
		for key, value in file_results.items():
			patterns_string = ""
			for pattern in file_results[ key ][ "patterns" ]:
				line_contents = file_results[ key ][ "line" ]
				patterns_string += pattern + ", "
				patterns_string = patterns_string[ :-2 ] # Removes last comma and space
				# Remove line breaks
				if line_contents.endswith( "\n" ):
					line_contents = line_contents[ :-1 ]
				elif line_contents.endswith( "\r" ):
					line_contents = line_contents[ :-1 ]
				elif line_contents.endswith( "\r\n" ):
					line_contents = line_contents[ :-2 ]
			self.results_output +=	" " * 3 + "%d: %s\n" % ( key, patterns_string )
			self.results_output +=	" " * 3 + "%s\n" % line_contents

	def show_results( self ):
		"""Prints analysis results"""
		print( "Analyzed files: %d" % self.analyzed_files )
		if len( self.results_found_patterns ) == 0:
			print( "No patterns found." )
			sys.exit()
		else:
			print( "Found patterns: %s \n" % self.get_string_from_dict( self.get_dictionary_sorted_by_key( self.results_found_patterns ) ) )
		print( self.results_output[ :-1 ] ) # Removes the last line break
		sys.exit()

	def get_file_found_patterns( self, file_results, pattern_name, matches_count ):
		"""Returns the number of matches of a pattern in a file"""
		if pattern_name not in file_results:
			return matches_count
		else:
			return file_results[ pattern_name ] + matches_count

	def get_string_from_dict( self, dictionary ):
		"""Converts dictionary to string"""
		return ", ".join( "{!s} ({!r})".format( key, value ) for ( key, value ) in dictionary.items() )

	def get_dictionary_sorted_by_key( self, dictionary ):
		"""Sorts dictionary by key"""
		return OrderedDict( sorted( dictionary.items(), key = lambda t:t[ 0 ] ) )

FileAnalyzer()
