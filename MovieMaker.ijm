// Movie maker
splitMovie = true;
addScalebar = true;
createCrop = true;
c1Name = "MS2";
c2Name = "SunTag";

// File open dialog
file = File.openDialog("Choose a File");
if (!File.exists(file)) {
	exit("Couldn't find file!");
}
run("Bio-Formats Importer", "open=" + file + " color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT");

// Split channels
baseName = File.getName(file);
if (splitMovie) {
	run("Duplicate...", "title=c1.tif duplicate range=1-15");
	selectWindow(baseName);
	run("Duplicate...", "title=c2.tif duplicate range=16-30");
	selectWindow(baseName);
	run("Close");
} else {
	run("Split Channels");
	selectWindow("C1-" + baseName);
	rename("c1.tif");
	selectWindow("C2-" + baseName);
	rename("c2.tif");
}

// Adjust brightness
run("Brightness/Contrast...");
waitForUser("Set contrast & brightness (with apply).\nClick 'OK' when done.");
run("Brightness/Contrast...");
run("Close");


// Create crops
if (createCrop) {
	selectWindow("c1.tif");
	waitForUser("Set ROI on c1 to crop.\nClick 'OK' when done.");
	Roi.getBounds(x, y, width, height);
	run("Crop");
	selectWindow("c2.tif");
	makeRectangle(x, y, width, height);
	run("Crop");
}

// Merge channels
run("Merge Channels...", "c2=c2.tif c6=c1.tif keep");
run("Stack to RGB", "frames");

// Add scale bar
if (addScalebar) {
	width = getNumber("Scale bar width (µm)", 50);
	run("Scale Bar...", "width=" + width + " height=5 font=0 color=White background=None location=[Lower Right] bold hide label");
}

// Create output movie
frames = nSlices;
width = getWidth;
height = getHeight;
newImage("new.tif", "RGB white", 8+width*3, height+40, frames);

for (i=1; i<=frames; i++) {
	// Paste individual movies
	setSlice(i);
	selectWindow("c1.tif");
	setSlice(i);
	run("Copy");
	selectWindow("new.tif");
	makeRectangle(0, 40, width, height);
	run("Paste");
	selectWindow("c2.tif");
	setSlice(i);
	run("Copy");
	selectWindow("new.tif");
	makeRectangle(width+4, 40, width, height);
	run("Paste");
	selectWindow("Merged");
	setSlice(i);
	run("Copy");
	selectWindow("new.tif");
	makeRectangle(2*width+8, 40, width, height);
	run("Paste");
	
	// Make black boxes above movies
	makeRectangle(0, 0, width, 36);
	run("Properties... ", "  fill=black");
	run("Add Selection...");
	makeRectangle(width+4, 0, width, 36);
	run("Properties... ", "  fill=black");
	run("Add Selection...");
	makeRectangle(2*width+8, 0, width, 36);
	run("Properties... ", "  fill=black");
	run("Add Selection...");
}

// Make labels for channels
setFont("SansSerif", 24, " antialiased");
setColor("magenta");
Overlay.drawString(c1Name, 90, 25, 0.0);
setColor("green");
Overlay.drawString(c2Name, width+77, 25, 0.0);
setColor("white");
Overlay.drawString("Merge", 2*width+90, 25, 0.0);
waitForUser("Check and center labels.\nClick 'OK' when done.");

// Save movies & close
splitFname = split(file, ".");
outFname = splitFname[0] + ".avi"; 
run("AVI... ", "compression=PNG frame=6 save="+outFname);
close("*");
