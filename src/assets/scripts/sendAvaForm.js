import { getCookie } from "./utils";
const sendAvaUpdate = function(url,avatar) {
    const fd = new FormData();
    fd.append("csrfmiddlewaretoken",getCookie("csrftoken"));
    fd.append('avatar',avatar)
    fetch(url,{
      method:"POST",
      body:fd
      }).then((resp)=>resp.json())
        .then((data)=>{
        if(data.status_code ===200){
           window.location.reload();
          }
        if(data.status_code ===404){
            // console.log("code 404; upload failed")
            jsErr.classList.remove("visually-hidden");
            jsErr.textContent = "Не получилось загрузить avatar";
            data.err.avatar.forEach((err)=>{
              let div = document.createElement("div")
              div.classList.add("errorlist");
              div.innerHTML = `${err}`;
              errDiv.appendChild(div)
            });
             throw new Error(message="Ошибка: файл не загружен");
            }
        })
        .catch((err)=>{
          console.log(err["message"])

     })
}
export {sendAvaUpdate}