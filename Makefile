build:
	@zip kwinscript.xpi -FS manifest.json background.js icons/*

clean:
	@rm -f kwinscript.xpi