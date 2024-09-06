import React, {useRef, useEffect} from 'react';


const Video = ({ src }) => {
    const videoRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (videoRef.current && !videoRef.current.contains(event.target)) {
                videoRef.current.controls = false;
            }
        };

        // Add event listener for clicks outside the video
        document.addEventListener('click', handleClickOutside);

        return () => {
            // Clean up event listener when the component unmounts
            document.removeEventListener('click', handleClickOutside);
        };
    }, []);

    return (
        <video
            ref={videoRef}
            onClick={(e) => {
                if (!e.target.controls) {
                    e.stopPropagation();  // Stop the click event from propagating
                    e.target.controls = !e.target.controls;
                }
               
            }}
            controls
            style={{ width: '100%', cursor: 'pointer' }}
            className="h-full w-full rounded-lg"
            loop
            muted
            autoPlay
            playsInline
            src={src}
        >
        </video>
    );
};

export default Video;