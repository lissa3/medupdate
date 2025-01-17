import { formatFileSize,checkExt,fileToDataUri,helpUtil } from "./utils";
import { sendAvaUpdate } from "./sendAvaForm";
const checkInp = (checkbox,inp)=>{
    /*
    func for upload image:
    1.should help to send only one state to the server:
    either remove avatar or update the old one;
    2.toggle class 'disabled' on submit button
     */
    if(checkbox){
         // checkbox(remove avatar) present in DOM:
        // checked vs unchecked
        checkbox.addEventListener("change",(e)=>{
          console.log("checkbox reacted!!!!!")
        if(checkbox.checked){
            // checkbox checked = avatar should be removed
          inp.value = null //
          butSubmit.classList.remove("disabled")
         } else{
          butSubmit.classList.add("disabled")
        }
       });
       inp.addEventListener("change",()=>{
        if(inp.value){
          checkbox.checked = false;
          butSubmit.classList.remove("disabled")
        }else{
          butSubmit.classList.add("disabled");
        }
      })
    }
    else{
    // checkbox present in DOM but not
    // state can contain either "remove img"
    // or "attach img" but not both
    if(checkbox!=null){
        // remove existed avatar (clear image input if user attached img occasionally);

        checkbox.addEventListener("change",(e)=>{
        if(checkbox.checked){
        inp.value = null
        butSubmit.classList.remove("disabled")
        }else{
        butSubmit.classList.add("disabled")
        }
        });
    inp.addEventListener("change",()=>{
        if(inp.value){
        checkbox.checked = false;
        butSubmit.classList.remove("disabled");
        }else{
        butSubmit.classList.add("disabled");
        }
    })
    }else{
    // checkbox NOT in DOM (avatar == default static image)
    inp.addEventListener("change",()=>{
    // toggle class 'disabled' on submit button
        if(inp.value){
        butSubmit.classList.remove("disabled")
        }else{
        butSubmit.classList.add("disabled")
        }
    })
   }
 }
}
// resize
let canvas,ctx,avatar,newImgUrl,serverErrMsg;
  const WIDTH = 600;
  const form = document.getElementById("upForm");
  if(form){
    const url = form.getAttribute("action");
    const checkbox = document.querySelector("#avatar-clear_id");
    const inp = document.querySelector("#imgInp");
    inp.innerHTML = "DDDDDDDDDDvxvxxvvx"
    console.log("line 77 here ")
    const butSubmit = document.querySelector("#butSubmit");
    const errDiv = document.querySelector("#errDiv");
    let jsErr = document.querySelector("#jsErr");
    // func to toggle class on inputs
    checkInp(checkbox,inp);
  document.addEventListener("DOMContentLoaded",init);
  function init(){
    canvas = document.createElement("canvas");
    ctx = canvas.getContext('2d');
    if(form){
      const url = form.getAttribute("action");
      form.addEventListener("submit",upload);
    }
  }
  async function upload(e){
    e.preventDefault()
    let file = inp.files[0];
    if(file){
      // file attached
      let userFileName = file.name;
      let initialSize = file.size;
      let humanSize = formatFileSize(file.size);
      let userFileExt = userFileName.split(".").at(-1).toLowerCase();
      console.log("file detected with extentions ",userFileExt)
      if(!checkExt(userFileExt)){
      // show error msg for 3 sec; clean file input and quit
      console.log("ext not right")
          jsErr.classList.remove("visually-hidden");
          console.log("jsErr removed vis hiddenp; adding msg")
          jsErr.textContent = "Only '.png/.jpeg/.jpg' file's extentions allowed";
          inp.value = null;
          setTimeout(()=>{
              jsErr.classList.add("visually-hidden");
              console.log("jsErr restoring class visually-hidden")
              jsErr.textContent = "";
          },3000)
        return;
      }
      const res = await fileToDataUri(file) // base64 encoded
      if(res){
        let img = new Image();
        img.src = res // base64 encoded
        img.onload = function(e){
          let initialHeight = img.height;
          let initialWidth = img.width;
          if(initialSize <300000)  {
          // file(less 300KB) without resizing
            sendAvaUpdate(url,avatar=file)
          }
          else if(initialWidth <WIDTH)  {
            // file (w < 600) without resizing
            sendAvaUpdate(url,avatar=file)
          }
          else{
      // resize the image
            console.log("try to resize")
            let scaleFactor = WIDTH/initialWidth;
            canvas.width = WIDTH;
            canvas.height = img.height * scaleFactor;
            ctx.drawImage(img,0,0,canvas.width,canvas.height);
            let newImgUrl = ctx.canvas.toDataURL("image/jpeg",0.9);
            avatar = helpUtil(newImgUrl,userFileName);
            sendAvaUpdate(url,avatar=avatar)
          }
        }
      }else{
      // error during reader file load
        jsErr.textContent = "Something went wrong; uplaod file failed"
        }
      }
      else{
      //file detached; remove existing avatar
      // console.log("file detached; removing exisitnig avatar")
      sendAvaUpdate(url,avatar=false);
    }
  }
}