function Message({userMessage,message,sources}) {
  return (
    <div className={`${userMessage ? "justify-end": "justify-start" } flex text-center font-semibold overflow-x-hidden h-full break-words`}>
      <div className={`${userMessage ? "bg-gradient-to-r from-blue-700 to-blue-400 text-white ": "bg-white text-black" } p-2 rounded-xl w-[50%] max-md:w-[85%] gap-2 overflow-x-hidden`}>
        <div className={`${!userMessage && "border-2 border-b-black border-transparent"} p-1`}>
          <p>{message}</p>
        </div>
        {!userMessage && (
          <div className='flex flex-row gap-2 my-2'>
            <div className='text-sm font-bold text-[#003D6D]'>
              <h1>Sources:</h1>
            </div>
            <div className='flex w-full gap-1 '>
              {sources.map((opt,idx)=>(
                <button 
                className={`px-2  text-sm text-center rounded-full   font-semibold bg-[#7F79F1]`  }
                key={`filters-${idx}`}>
                      {opt}
              </button>
              ))}
            </div>
            </div>
        )}
      </div>
    </div>
  )
}

export default Message
