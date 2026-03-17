export default function XrayPage() {
  return (
    <div className="grid grid-cols-3 gap-6 p-6">

      {/* Upload */}
      <div className="bg-white rounded-2xl shadow p-6 flex flex-col items-center">
        <h2 className="font-semibold mb-4">Upload</h2>

        <div className="w-full h-56 border-2 border-dashed border-gray-300 rounded-xl flex flex-col items-center justify-center">
          <p>Image</p>
          <input type="file" className="mt-2" />
        </div>
      </div>

      {/* Patient */}
      <div className="bg-white rounded-2xl shadow p-6">
        <h2 className="font-semibold mb-4">Patient History</h2>

        <p className="text-sm text-gray-400 mb-2">optional</p>

        <input placeholder="Age" className="w-full border p-2 rounded mb-2" />
        <input placeholder="Sex" className="w-full border p-2 rounded mb-2" />
        <input placeholder="Name" className="w-full border p-2 rounded mb-2" />

        <textarea placeholder="Preventions" className="w-full border p-2 rounded mt-2" />
        <textarea placeholder="Cases" className="w-full border p-2 rounded mt-2" />
      </div>

      {/* GradCAM */}
      <div className="bg-white rounded-2xl shadow p-6">
        <h2 className="font-semibold mb-4">Grad-CAM Analysis</h2>

        <div className="h-56 bg-gray-100 rounded-xl flex items-center justify-center text-gray-400">
          Python output here
        </div>
      </div>

      {/* Report */}
      <div className="col-span-3 bg-white rounded-2xl shadow p-6">
        <h2 className="font-semibold mb-2">Report</h2>

        <div className="h-28 bg-gray-100 rounded-xl flex items-center justify-center text-gray-400">
          API se milega
        </div>
      </div>

    </div>
  )
}
