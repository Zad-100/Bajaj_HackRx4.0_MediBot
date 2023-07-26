import { useState,useEffect } from 'react';

import chat from '../assets/Chat.svg';
import mic from '../assets/Mic.svg';
import fileAdd from '../assets/File_dock_add.svg';
import send from '../assets/Send_hor.svg'


function ChatBox({sources,messages,setMessages,reply,setReply}) {

  const [showSendIcon,setShowSendIcon] = useState(false);
  const [enteredInput,setEnteredInput]=useState("");
  
    const messageHandler = (e) =>{
        setEnteredInput(e.target.value);
    }

    const host = 'http://localhost:5000'

    const fetchData = async () => {
      try {
        const response = await fetch(`${host}/run_medibot`,
        {
          method: 'get'
        })
        const data = await response.json();
        setMessages([...messages,{sources,"message":enteredInput}])
        setReply([...reply,{"reply":data['response'],"sources":data['source_cites']}])
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    }

    const sendHandler = async () => {
      if (!sources.length) {
        alert('Please select a Source.')
        return
      }
      if (enteredInput.length == 0) return

      try {
        const response = await fetch(`${host}/upload_sources`,
        {
          method: 'post',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({'source': sources})
        })
        if (!response.ok) throw new Error('Something went wrong!')
        
        const response2 = await fetch(`${host}/patient_query`,
        {
          method: 'post',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({'query': enteredInput})
        })
        if (!response2.ok) throw new Error('Something went wrong!')
      } catch(error) {
        console.log(error)
      }
      await fetchData()
      setEnteredInput("")
      setTimeout(async () => {
        const rating = parseInt(prompt("Rate the response (out of 5)", "5"))
        if (isNaN(rating) || rating < 0 || rating > 5) return
        try {
          const response = await fetch(`${host}/feedback`,
          {
            method: 'post',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'rating': rating})
          })
          if (!response.ok) throw new Error('Something went wrong!')
        } catch(error) {
          console.log(error)
        }
      }, 5000)
    }

    useEffect(()=>{
        if (enteredInput.length==0) setShowSendIcon(false)
        else setShowSendIcon(true)
    }, [enteredInput])

  return (
    <div>
      <div className='flex gap-2 bg-white mx-8 rounded-full justify-between p-2'>
        <div className='flex flex-row gap-3 w-full'>
            <img src={chat} />
            <input type='text' placeholder='Let’s talk medical...' className='focus:outline-0 border-none w-[95%]'
            onChange={messageHandler} value={enteredInput} />
        </div>
        {showSendIcon ? (
            <div>
                <button onClick={sendHandler}>
                  <img src={send} />
                </button>
            </div> ):( 
            <div className="flex gap-2">
            <img src={fileAdd} className='cursor-pointer'/>
            <img src={mic} className='cursor-pointer'/>
            </div>
        )}
        
      </div>
    </div>
  )
}

export default ChatBox
