function formatBytes (bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes'
      const k = 1024
      const dm = decimals < 0 ? 0 : decimals
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
  }
  function formatFileSize(size){
      var sizes = [' Bytes', ' KB', ' MB', ' GB', ' TB', ' PB', ' EB', ' ZB', ' YB'];
      for (let i = 1; i < sizes.length; i++)
      {
          if (size < Math.pow(1024, i)) {
            return (Math.round((size/Math.pow(1024, i-1))*100)/100) + sizes[i-1];
          }
      }
      return size;
    }
  //   option N1 ()
  const getCsrfToken = () => {
      return document.querySelector('[name=csrfmiddlewaretoken]').value
    }
  // option N2
  function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
              const cookie = cookies[i].trim();
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, name.length + 1) === (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
  }

  let helpUtil =  (url,name)=>{
    /*
    func: convert base64 format to File;
    return file with initial name and mime type
    */
    let arr = url.split(",")
    let mime = arr[0].match(/:(.*?);/)[1]
    let dataStr = arr.at(-1)
    // let dataStr = arr[1]
    let bstr = atob(dataStr);
    let lenData = bstr.length;
    const u8arr = new Uint8Array(lenData)
    while(lenData--){
        u8arr[lenData]= bstr.charCodeAt(lenData);
    }
    const file = new File([u8arr],name,{type:mime})
    return file;
  }

  const checkExt = (fileExt)=>{
    const  ALLOWED = ["jpg","jpeg","png"]
    return ALLOWED.includes(fileExt);
  }

  function fileToDataUri(file) {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.addEventListener("load", () => {
        resolve(reader.result);
      });
      reader.readAsDataURL(file);
    });
  }
// button to the topFunction//Get the button
const toTop = document.getElementById("toTop");
  // When the user scrolls down 20px from the top of the document, show the button
if(toTop){
  window.onscroll = function() {scrollFunction()};

function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 60) {
      toTop.style.display = "block";
    } else {
      toTop.style.display = "none";
    }
  }
  // When the user clicks on the button, scroll to the top of the document
  toTop.addEventListener("click",(e)=>{
    // click to the top
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
  })
}
export {getCookie,formatBytes,formatFileSize,checkExt,fileToDataUri,helpUtil}