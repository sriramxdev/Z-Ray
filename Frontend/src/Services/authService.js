// import API from "./api"

// export const loginUser = async(email,password)=>{

// const res = await API.post("/auth/login",{
// email,
// password
// })

// localStorage.setItem("token",res.data.token)

// return res.data

// }

export const loginUser = async (email, password) => {

if(email === "doctor@test.com" && password === "123456"){

localStorage.setItem("token","testtoken")

return {success:true}

}

throw new Error("Invalid Login")

}