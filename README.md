# X-Ray Calibre Plugin
Downloads:
----------------------------------------------------------------------------------------------------------------------------------
[3.0.1](https://github.com/szarroug3/X-Ray_Calibre_Plugin/blob/master/Versions/xray_creator_calibre_plugin_3_0_1.zip?raw=true)

[3.0.0](https://github.com/szarroug3/X-Ray_Calibre_Plugin/blob/master/Versions/xray_creator_calibre_plugin_3_0_0.zip?raw=true)

[2.2.1](https://github.com/szarroug3/X-Ray_Calibre_Plugin/blob/master/Versions/xray_creator_calibre_plugin_2_2_1.zip?raw=true)

[2.2.0](https://github.com/szarroug3/X-Ray_Calibre_Plugin/blob/master/Versions/xray_creator_calibre_plugin_2_2_0.zip?raw=true)

[2.1.2](https://github.com/szarroug3/X-Ray_Calibre_Plugin/blob/master/Versions/xray_creator_calibre_plugin_2_1_2.zip?raw=true)

[2.1.1](https://github.com/szarroug3/X-Ray_Calibre_Plugin/blob/master/Versions/xray_creator_calibre_plugin_2_1_1.zip?raw=true)

[2.1.0](https://github.com/szarroug3/X-Ray_Calibre_Plugin/blob/master/Versions/xray_creator_calibre_plugin_2_1_0.zip?raw=true)

[2.0.0](https://github.com/szarroug3/X-Ray_Calibre_Plugin/blob/master/Versions/xray_creator_calibre_plugin_2_0_0.zip?raw=true)

[1.1.0](https://github.com/szarroug3/X-Ray_Calibre_Plugin/blob/master/Versions/xray_creator_calibre_plugin_1_1_0.zip?raw=true)

[1.0.0](https://github.com/szarroug3/X-Ray_Calibre_Plugin/blob/master/Versions/xray_creator_calibre_plugin_1_0_0.zip?raw=true)

Websites:
----------------------------------------------------------------------------------------------------------------------------------
Github Page: https://github.com/szarroug3/X-Ray_Calibre_Plugin

Mobileread Page: http://www.mobileread.com/forums/showthread.php?p=3301947#post3301947

Some background information on X-Ray:
----------------------------------------------------------------------------------------------------------------------------------
X-Ray files allow you to get information on key characters and terms from Goodreads. You can do this in one of a few ways.
1. You can highlight the word in question and if the x-ray file has information on it, a popup with a brief description will
	show. It will also show you where this character has been mentioned in the past (will show page number and excerpt where
	mention occurred).
2. You can click X-Ray and search for the word either by looking through the list or using the search bar. Clicking on the word
	will show you the same popup from #1.

Note: X-Ray files work only work on Amazon products such as the Kindle PW. For more information on X-Ray files, see here:
	http://www.amazon.com/gp/help/custom...7-239A35EB4119
It also has a notable clips section which show quotes from Goodreads. If there are not enough Goodreads quotes found, the plugin
	will add more random excerpts so there are least 20 notable clips.
Github Page: https://github.com/szarroug3/X-Ray_Calibre_Plugin

----------------------------------------------------------------------------------------------------------------------------------
	1. Book specific preferences
		- Use "," or ", " as a separator for words in aliases list
	2. Create/Update x-ray files for selected books
	3. Send previously generated x-ray files to device
	4. General Preferences

	Note: Creating an x-ray file using this plugin will use the ASIN already in the book so you don't need to update it.
	Note: Highlighting words should work but I have not tested with a book that has DRM so I don't know if it will work for them.

Preferences:
----------------------------------------------------------------------------------------------------------------------------------
	1. Send x-ray to device if connected
		- After creating x-ray file, file will automatically be sent to device
	2. Create x-ray for files that don't already have them when sending to device
		- When sending previously generated x-ray files, x-ray files will be generated for selected books that don't already have
			a file created
	3. Auto associate split aliases, when enabled, will split aliases retrieved from Goodreads up
		- i.e If a character on goodreads named "Vin" has a Goodreads alias of "Valette Renoux", this option will add
			"Valette" and "Renoux" as aliases. You may not want this in cases such as "Timothy Cratchit" who has a
			Goodreads alias of "Tiny Tim". Having this feature on would add "Tiny", and "Tim" as
			aliases which is not valid.
	4. Overwrite local files that already exist when creating files
		- When using the Create/Update Files function, this will decide whether or not to delete local files that already exist
	5. Overwrite files on device that already exist when sending files
		- When using the Send Files function, this will decide whether or not to delete files on the device that already exist
	6. Files to create/send
		- This will let you choose what type of files to create and/or send
		- You must choose at least one.
	7. Book types to create x-ray files for
		- Selection of formats to consider when creating and sending x-ray files.
		- You must choose at least one.
	8. If device has both (mobi and azw3) formats, prefer
		- This will choose which format to send x-ray files for if your device has both file formats
		- This matters because there are offsets in the x-ray file that determine whether something that is highlighted is
			part of the x-ray
		- If you are sure you only have one format of the book type on the device, this does not matter.

Testing:
----------------------------------------------------------------------------------------------------------------------------------
	This plugin has been tested using a Kindle PW2 on Windows 10 and Linux.
	We are still actively developing the plugin so if you do find a bug or want to request a feature, please let me know via
		Github or Mobileread.
