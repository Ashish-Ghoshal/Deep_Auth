// Initializes camera settings and attaches it to the DOM element
function initializeWebcam() {
    setupWebcamSettings();
    attachWebcamToElement("#camera_view");
}

// Sets up webcam configuration parameters
function setupWebcamSettings() {
    Webcam.set({
        height:  500,
        width: 600,
        jpeg_quality: 90,
        dest_width: 300,
        dest_height: 400,
        image_format: 'jpeg'
        
    });
}


// Attaches webcam to a specific element on the page
function attachWebcamToElement(elementSelector) {
    Webcam.attach(elementSelector);
}

// Takes a snapshot and processes the image data
function captureSnapshot() {
    triggerEffectOnSnapshot();
    hideCaptureButton();
    
    Webcam.snap(function(data_uri) {
        processCapturedImage(data_uri);
        storeCapturedImage(data_uri);
    });
}

// Adds a visual effect when the snapshot is taken
function triggerEffectOnSnapshot() {
    document.getElementById('camera_view').classList.toggle("effect");
}

// Hides the capture button after the snapshot is taken
function hideCaptureButton() {
    document.getElementById("generateEmbeddingsBtn").style.display = "none";
}

// Processes and displays the captured image on the page
function processCapturedImage(imageData) {
    displayImageThumbnail(imageData);
}

// Stores the captured image in a list
function storeCapturedImage(imageData) {
    storedImagesList.push(imageData);
    updateStoredImagesCount();
    saveImagesToLocalStorage(storedImagesList);
}

// Displays a thumbnail of the captured image
function displayImageThumbnail(imageData) {
    var imgElement = document.createElement('li');
    imgElement.innerHTML = '<img class="thumbnail" src="' + imageData + '"/>';
    document.getElementById('image_list').insertBefore(imgElement, null);
}

// Updates the count of stored images and modifies the UI accordingly
function updateStoredImagesCount() {
    if (storedImagesList.length > 0) {
        document.getElementById("image_status").innerHTML = storedImagesList.length + " image" + (storedImagesList.length > 1 ? "s" : "") + " stored.";

        if (checkIfMaxImagesStored(storedImagesList)) {
            disableSnapshotUI();
            displayMaxImagesAlert();
        } else {
            enableSnapshotUI();
        }
    } else {
        document.getElementById("image_status").innerHTML = "No images stored.";
    }
}

// Checks if the maximum number of images is stored
function checkIfMaxImagesStored(imageArray) {
    return Array.isArray(imageArray) && imageArray.length == 8;
}

// Disables the snapshot UI after maximum images are stored
function disableSnapshotUI() {
    document.getElementById('captureDiv').style.display = 'none';
    document.getElementById("generateEmbeddingsBtn").style.display = "block";
}

// Enables the snapshot UI
function enableSnapshotUI() {
    document.getElementById('captureDiv').style.display = 'block';
}

// Displays an alert when maximum images are stored
function displayMaxImagesAlert() {
    Swal.fire({
        title: '<strong>Only 8 snaps allowed</strong>',
        icon: 'info',
        showCloseButton: true,
        showCancelButton: true,
        confirmButtonText: '<i class="fa fa-thumbs-up"></i> Great!',
    });
}

// Removes all stored images
function clearStoredImages() {
    storedImagesList = [];
    localStorage.removeItem("images");
    resetImageListUI();
}

// Resets the image list in the UI
function resetImageListUI() {
    document.getElementById('image_list').innerHTML = "";
    document.getElementById("generateEmbeddingsBtn").style.display = "none";
}

// Loads images from local storage
function loadImagesFromLocalStorage() {
    var images = JSON.parse(localStorage.getItem("images"));
    if (images && images.length > 0) {
        storedImagesList = images;
        updateStoredImagesCount();
        images.forEach(displayImageThumbnail);
    }
}

// Posts the image data for processing
function submitImageData(actionType) {
    Swal.fire({
        imageUrl: 'https://i.gifer.com/DzUh.gif',
        imageWidth: 400,
        imageHeight: 200,
        showConfirmButton: false
    });

    var images = JSON.parse(localStorage.getItem("images"));
    var formData = createFormData(images);
    
    submitFormData(actionType, formData);
}

// Creates form data from images
function createFormData(images) {
    var formData = {};
    images.forEach(function(image, index) {
        var strippedImage = stripImagePrefix(image);
        formData["image" + (index + 1)] = strippedImage;
    });
    return formData;
}

// Strips the data URI prefix from the image
function stripImagePrefix(imageData) {
    return imageData.replace(/^data:image\/[a-z]+;base64,/, "");
}

// Submits the form data based on the action type
function submitFormData(actionType, formData) {
    var targetUrl = (actionType == 'login') ? '/application/' : '/application/register_embedding';
    var formElement = createFormElement(targetUrl, formData);
    
    document.body.appendChild(formElement);
    formElement.submit();
}

// Creates a hidden form element with the form data
function createFormElement(actionUrl, formData) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = actionUrl;
    Object.keys(formData).forEach(function(key) {
        const hiddenField = document.createElement('input');
        hiddenField.type = 'hidden';
        hiddenField.name = key;
        hiddenField.value = formData[key];
        form.appendChild(hiddenField);
    });
    return form;
}

// Main execution
document.getElementById('clearImagesBtn').addEventListener("click", clearStoredImages);
loadImagesFromLocalStorage();
document.getElementById("generateEmbeddingsBtn").style.display = "none";
