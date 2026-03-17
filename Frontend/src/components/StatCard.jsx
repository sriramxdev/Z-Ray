function StatCard({title,value}){

return(

<div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">

<h3 className="text-gray-500">{title}</h3>

<p className="text-3xl font-bold text-blue-600 mt-2">
{value}
</p>

</div>

)

}

export default StatCard