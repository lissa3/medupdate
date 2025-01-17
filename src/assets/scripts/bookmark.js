import { getCookie } from "./utils";
// func to add/remove bookmarks
const jsBox = document.getElementById("jsBox");
const formBook = document.querySelector("#bookmark");
const bmarkDiv = document.getElementById("bmarkDiv");

if(bmarkDiv&& formBook){
  //func for adding bookmark via ajax
  const fd = new FormData();
  fd.append("csrfmiddlewaretoken",getCookie("csrftoken"))
  formBook.addEventListener("submit",(e)=>{
    e.preventDefault();
    const url = formBook.getAttribute("action");
    fd.append("post_uuid",formBook.post_uuid.value);
    fd.append("profile_uuid",formBook.profile_uuid.value);
    fetch(url,{
      method:"POST",
      headers:{ "x-requested-with": "XMLHttpRequest"},
      body:fd
      }).then((resp)=>resp.json())
        .then((data)=>{
          if(data.status_code ===200){
            let msg = data.msg;
             //  add success flash msg
            jsBox.classList.add("green","custom-slide");
            jsBox.textContent=  msg;
            if(data.del_button){
              bmarkDiv.remove();
            }
          }
          else if(data.status_code ===404){
            //  add error flash msg
              jsBox.classList.add("red","custom-slide");
              jsBox.textContent= "Failed to add to bookmarks";
            throw new Error(message="Failed to add to bookmarks");
          }
        })
        .catch((err)=>{
          console.log(err["message"]);
        })
  })
}