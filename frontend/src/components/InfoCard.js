function InfoCard({image,head,paragraph}) {
  return (
    <div className=' flex flex-col justify-center-items-center lg:gap-4 gap-1'>
      <div className='flex flex-row justify-center font-bold'>
        <img src={image} />
        <h1 className='text-sm'>{head}</h1>
      </div>
        <p className='text-xs md:h-[7em] rounded-md bg-white  text-center p-5 shadow-lg'>{paragraph}</p>
    </div>
  )
}

export default InfoCard
