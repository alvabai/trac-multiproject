/*
	A simple class for displaying file information and progress
	Note: This is a demonstration only and not part of SWFUpload.
	Note: Some have had problems adapting this class in IE7. It may not be suitable for your application.
*/

// Constructor
// file is a SWFUpload file object
// targetID is the HTML element id attribute that the FileProgress HTML structure will be added to.
// Instantiating a new FileProgress object with an existing file will reuse/update the existing DOM elements
function FileProgress(file, targetID) {
	this.fileProgressID = file.id;

	this.opacity = 100;
	this.height = 0;
	
  /* Check if there already is this file to be downloaded? */
	this.fileProgressWrapper = document.getElementById(this.fileProgressID);

	if (!this.fileProgressWrapper) {

    /* main element containing the progress bar */
		this.fileProgressWrapper = document.createElement("div");
    this.fileProgressWrapper.className = "progressWrapper";
    this.fileProgressWrapper.id = this.fileProgressID;

    /* Element inside wrapper */
		this.fileProgressElement = document.createElement("div");
    this.fileProgressElement.className = "progressContainer";

    this.fileProgressWrapper.appendChild(this.fileProgressElement);

		document.getElementById(targetID).appendChild(this.fileProgressWrapper);


    /* left and right round corners */
    var progressContElem = '#'+this.fileProgressID + ' .progressContainer';
    
    $(progressContElem).append ("<div class='pbarleft'></div>")
    $(progressContElem).append ("<div class='pbarright'></div>")
    $(progressContElem).append ("<div class='progressBarBG'></div>")

    /* progress bar round corners */
    var progressBarBGElem = '#'+this.fileProgressID + ' .progressBarBG';
    $(progressBarBGElem).append ("<div id = 'progbarleft' class='progbarleft'></div>")
    $(progressBarBGElem).append ("<div id = 'progbarright' class='progbarright'></div>")

    /* Cancel button */
    $(progressContElem).append ("<a class='progressCancel' href='#'>Remove<span class='delete_button' style='margin-left:5px;padding-left:20px;'></span></a>")

    /* File name */
    var filename = file.name;
    if (filename.length > 18) {
      filename = filename.substring(0, 18);
      filename += "...";
    }
    $(progressContElem).append ("<div class='progressName'>"+ filename + "</div>")

    /* Progress bar background and the actual progress bar */
    $(progressBarBGElem).append ("<div class = 'progBarUploading' id='progressBar' style='width:0px;min-height:23px;float:left;background:#305295;position:absolute;left:0px;top:0px'></div>")

    var progressBarElem = '#'+this.fileProgressID + ' #progressBar';
    $(progressBarElem).append ("<span class = 'status'>Pending</span>")
    $(progressBarElem).append ("<div id = 'progbarleftB' class='progbarleftB'></div>")
    $(progressBarElem).append ("<div id = 'progbarrightB' class='progbarrightB'></div>")


	} else {
		this.fileProgressElement = this.fileProgressWrapper.firstChild;
		this.reset();
	}

	this.height = this.fileProgressWrapper.offsetHeight;
	this.setTimer(null);
}

FileProgress.prototype.setTimer = function (timer) {
	this.fileProgressElement["FP_TIMER"] = timer;
};

FileProgress.prototype.getTimer = function (timer) {
	return this.fileProgressElement["FP_TIMER"] || null;
};

FileProgress.prototype.reset = function () {
  this.fileProgressElement.className = "progressContainer";

  this.appear();  
};

FileProgress.prototype.setProgress = function (percentage) {
  this.fileProgressElement.className = "progressContainer blue";

  var findstr = "#" + this.fileProgressID + " #progressBar";
  $(findstr).removeClass().addClass ('progressBarUploading');

  width = 650/100*percentage;
  var widthstr = width + "px";
  $(findstr).css('width', widthstr);

  /* at start fill the left round corner */
  if (percentage > 0) {
    var findstr = "#" + this.fileProgressID + " #progbarleftB";
    $(findstr).css('visibility', 'visible');
    var findstr = "#" + this.fileProgressID + " #progbarleft";
    $(findstr).css('display', 'none');
  }
  /* at the end fill the right round corner */
  if (percentage == 100) {
    var findstr = "#" + this.fileProgressID + " #progbarrightB";
    $(findstr).css('visibility', 'visible');
    var findstr = "#" + this.fileProgressID + " .progbarright";
    $(findstr).css('display', 'none');
  }

  this.setStatus ("Uploading " + percentage + "%");

	this.appear();	
};

FileProgress.prototype.setComplete = function () {
  this.fileProgressElement.className = "progressContainer blue";
  var findstr = "#" + this.fileProgressID + " #progressBar";
  $(findstr).removeClass().addClass ('progressBarComplete');
  $(findstr).css('width', '650px');

  var findstr = "#" + this.fileProgressID + " .progbarright";
  $(findstr).css('display', 'none');

  this.setStatus ("Complete");

	var oSelf = this;
	this.setTimer(setTimeout(function () {
		oSelf.disappear();
	}, 5000));
};

FileProgress.prototype.setError = function () {
  this.fileProgressElement.className = "progressContainer blue";
  var findstr = "#" + this.fileProgressID + " #progressBar";
  $(findstr).removeClass().addClass ('progressBarError');
  $(findstr).css('width', '650px');

  var findstr = "#" + this.fileProgressID + " .progbarright";
  $(findstr).css('display', 'none');

  this.setStatus ("Error");

  var oSelf = this;
  this.setTimer(setTimeout(function () {
    oSelf.disappear();
  }, 60000));
};

FileProgress.prototype.setCancelled = function () {

  this.fileProgressElement.className = "progressContainer";
  var findstr = "#" + this.fileProgressID + " #progressBar";
  $(findstr).removeClass().addClass ('progressBarError');
  $(findstr).css('width', '0%');
  this.setStatus ('Cancelling...');  
	
	var oSelf = this;
	this.setTimer(setTimeout(function () {
		oSelf.disappear();
	}, 1000));
};

FileProgress.prototype.setStatus = function (status, color) {
  var findstr = "#" + this.fileProgressID + " .status";
  if (color == '') {
    color = '#AAAAAA';
  }
  $(findstr).css ('color',color)
  $(findstr).html(status);
};

// Show/Hide the cancel button
FileProgress.prototype.toggleCancel = function (show, swfUploadInstance) {
  var findstr = "#" + this.fileProgressID + " .progressCancel";
	$(findstr).css('visibility', show ? 'visible':'hidden');
	if (swfUploadInstance) {
		var fileID = this.fileProgressID;
		this.fileProgressElement.childNodes[3].onclick = function () {
			swfUploadInstance.cancelUpload(fileID);
			return false;
		};
	}
};

FileProgress.prototype.appear = function () {
	if (this.getTimer() !== null) {
		clearTimeout(this.getTimer());
		this.setTimer(null);
	}
	
	if (this.fileProgressWrapper.filters) {
		try {
			this.fileProgressWrapper.filters.item("DXImageTransform.Microsoft.Alpha").opacity = 100;
		} catch (e) {
			// If it is not set initially, the browser will throw an error.  This will set it if it is not set yet.
			this.fileProgressWrapper.style.filter = "progid:DXImageTransform.Microsoft.Alpha(opacity=100)";
		}
	} else {
		this.fileProgressWrapper.style.opacity = 1;
	}
		
	this.fileProgressWrapper.style.height = "";
	
	this.height = this.fileProgressWrapper.offsetHeight;
	this.opacity = 100;
	this.fileProgressWrapper.style.display = "";
	
};

// Fades out and clips away the FileProgress box.
FileProgress.prototype.disappear = function () {

	var reduceOpacityBy = 15;
	var reduceHeightBy = 4;
	var rate = 30;	// 15 fps

	if (this.opacity > 0) {
		this.opacity -= reduceOpacityBy;
		if (this.opacity < 0) {
			this.opacity = 0;
		}

		if (this.fileProgressWrapper.filters) {
			try {
				this.fileProgressWrapper.filters.item("DXImageTransform.Microsoft.Alpha").opacity = this.opacity;
			} catch (e) {
				// If it is not set initially, the browser will throw an error.  This will set it if it is not set yet.
				this.fileProgressWrapper.style.filter = "progid:DXImageTransform.Microsoft.Alpha(opacity=" + this.opacity + ")";
			}
		} else {
			this.fileProgressWrapper.style.opacity = this.opacity / 100;
		}
	}

	if (this.height > 0) {
		this.height -= reduceHeightBy;
		if (this.height < 0) {
			this.height = 0;
		}

		this.fileProgressWrapper.style.height = this.height + "px";
	}

	if (this.height > 0 || this.opacity > 0) {
		var oSelf = this;
		this.setTimer(setTimeout(function () {
			oSelf.disappear();
		}, rate));
	} else {
		this.fileProgressWrapper.style.display = "none";
		this.setTimer(null);
	}
};
