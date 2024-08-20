'use client'

import React, { useState } from 'react';
import { Suspense } from 'react';
import Video from '@/components/Video';
import { Container, Typography, Button, FormControl, FormLabel, RadioGroup, FormControlLabel, Radio, Slider, Checkbox, IconButton, Modal, Box } from '@mui/material';
import { Snackbar, Alert, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';

import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from "@hookform/resolvers/yup"
import * as yup from "yup"
import { storeAnnotation } from '@/lib/actions';
// import { useRouter } from 'next/navigation';

const questions = [
    {
        id: 'pixel_quality',
        label: "How would you rate the overall video resolution and sharpness?",
        min: 0,
        max: 5
    },
    {
        id: 'object_presence',
        label: "How clearly visible are the primary objects involved in the action?",
        min: 0,
        max: 5
    },
    {
        id: 'action_completeness',
        label: "How completely does the video segment capture the entire action, including the beginning and end?",
        min: 0,
        max: 5
    },
    {
        id: 'distractions',
        label: "To what extent does the video successfully maintain focus on the action, minimizing the impact of distracting objects or movements in the background?",
        min: 0,
        max: 5
    }
]


const schema = yup
    .object({
        ...questions.reduce((acc, q) => {
            acc[q.id] = yup.number().integer().required();
            return acc;
        }, {})
        // narrationClarity1: yup.number().integer().required(),
        // narrationClarity2: yup.number().integer().required(),
        // narrationClarity3: yup.number().integer().required(),
        // narrationClarity4: yup.number().integer().required(),
        // narrationClarity5: yup.number().integer().required(),
        // narrationConsistency: yup.bool().required(),
        // narrationEngagement: yup.number().required(),
    })
    .required()


const defaultValues = questions.reduce((acc, q) => {
    acc[q.id] = '';
    return acc;
}, {});


export default function Annotate({ file, annotation, allCount, completeCount }) {
    // const router = useRouter();
    const [openSnackbar, setOpenSnackbar] = useState(false);
    const [openDialog, setOpenDialog] = useState(false);
    const [counts, setCounts] = useState({allCount, completeCount})


    const goToRandomAnnotation = () => {
        window.location.href = '/annotate/random';
    };
    const {
        control,
        handleSubmit,
        formState: { errors },
    } = useForm({
        resolver: yupResolver(schema),
        defaultValues: {
            ...defaultValues,
            ...annotation
        },
        // defaultValues: {
        //     ...defaultValues
        //     // narrationClarity1: '',
        //     // narrationClarity2: '',
        //     // narrationClarity3: '',
        //     // narrationClarity4: '',
        //     // narrationClarity5: '',
        //     // narrationConsistency: '',
        //     // narrationEngagement: '',
        // },
    });

    const onSubmit = (data) => {
        console.log('Form Data:', data);
        // const annotations = JSON.parse(localStorage.getItem('annotations') || '{}');
        // annotations[file.narration_id] = data;
        // localStorage.setItem('annotations', JSON.stringify(annotations));

        // storeAnnotation(file.narration_id, data)
        // Close the dialog before proceeding with submission
        setOpenDialog(false);

        storeAnnotation(file.narration_id, data)
            .then(({allCount, completeCount}) => {
                // console.log(res);
                setCounts({allCount, completeCount});
                setOpenSnackbar(true); // Show success snackbar after submission
            })
            .catch(error => {
                console.error("Error saving annotation:", error);
            });
        // You can handle form submission logic here, like sending data to a server
    };

    const handleSaveClick = () => {
        setOpenDialog(true); // Open the confirmation dialog when Save is clicked
    };

    const handleDialogClose = (confirm) => {
        setOpenDialog(false);

        if (confirm) {
            handleSubmit(onSubmit)(); // Proceed with form submission if confirmed
        } else {
            // setOpenDialog(false); // Close the dialog if canceled
        }
    };


    const [openHelp, setOpenHelp] = useState(false);

    const handleHelpOpen = () => setOpenHelp(true);
    const handleHelpClose = () => setOpenHelp(false);

    return (
        <main className="flex min-h-screen flex-col items-center justify-center m-4 pb-16">
            {/* Sticky container with video and task description side by side */}
            <div className="flex-grow w-full max-w-5xl space-y-4"
            // style={{ position: 'sticky', top: 20, flexShrink: 0, zIndex: 999 }}
            >
                {/* <Typography variant="h5" component="h1" gutterBottom>
                    Annotate Video Segment Quality
                </Typography> */}
                <h2 className="text-2xl sm:text-3xl font-extrabold">Annotate</h2>

                <Suspense fallback={<div>Loading...</div>}>
                    <>
                        <div className='my-2'>
                            <div className='mr-3 inline'>
                                Completed: {counts.completeCount}/{counts.allCount}
                            </div>
                        </div>
                        <div className='my-2'>
                            <div className='mr-3 inline'>
                                Narration ID: <span className="p-2 bg-red-500 text-white">{file.narration_id}</span>
                            </div>
                            <div className='mr-3 inline'>
                                Action Label: <span className="p-2 bg-red-500 text-white">{file.narration}</span>
                            </div>
                        </div>

                        <Video src={file.url} />

                    </>

                </Suspense>

                <div style={{ flexGrow: 1 }}>
                    <Typography variant="h6" component="h2">
                        Annotation task description
                        <IconButton aria-label="help" onClick={handleHelpOpen} style={{ marginLeft: 8 }}>
                            <HelpOutlineIcon />
                        </IconButton>
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                        {/* Please watch the video and answer the following questions based on your observations. */}
                        Your task is to carefully watch the provided video segment and answer a series of questions that assess the clarity, completeness, and quality of the actions depicted.
                    </Typography>
                </div>

                {/* Annotation Form */}
                <form onSubmit={handleSubmit(onSubmit)} className='flex flex-col w-full items-start justify-start pt-4'>

                    <div className='text-red-400'>
                        {Object.keys(errors).length > 0 && "Please complete all questions before saving"}
                    </div>


                    {/* Repeat for other Multiple Choice Questions */}
                    {questions.map((q) => (
                        <FormControl component="fieldset" className="mt-4" key={q.id}>
                            <FormLabel component="legend">{q.label}</FormLabel>
                            <Controller
                                name={q.id}
                                control={control}
                                render={({ field }) => (
                                    <RadioGroup row {...field}>
                                        <FormControlLabel value="0" control={<Radio />} label="0" />
                                        <FormControlLabel value="1" control={<Radio />} label="1" />
                                        <FormControlLabel value="2" control={<Radio />} label="2" />
                                        <FormControlLabel value="3" control={<Radio />} label="3" />
                                        <FormControlLabel value="4" control={<Radio />} label="4" />
                                        <FormControlLabel value="5" control={<Radio />} label="5" />
                                    </RadioGroup>
                                )}
                            />
                        </FormControl>
                    ))}

                    {/* Boolean Question */}
                    {/* <FormControl component="fieldset" className="mt-4">
    <FormLabel component="legend">Was the narration consistent?</FormLabel>
    <Controller
        name="narrationConsistency"
        control={control}
        render={({ field }) => (
            <FormControlLabel
                control={<Checkbox {...field} checked={field.value} />}
            // label="Was the narration consistent?"
            />
        )}
    />
</FormControl> */}

                    {/* Slider Question */}
                    {/* <FormControl component="fieldset" className="mt-4">
    <FormLabel component="legend">How engaging was the narration? (0-1)</FormLabel>
    <Controller
        name="narrationEngagement"
        control={control}
        render={({ field }) => (
            <Slider {...field} value={field.value} step={0.1} min={0} max={1} marks valueLabelDisplay="on" />
        )}
    />
</FormControl> */}

                    {/* Submit Button */}
                    <div
                        className='flex space-x-4'
                        style={{
                            position: 'fixed',
                            bottom: '20px',
                            right: '20px',
                            zIndex: 1000,
                        }}
                    >
                        <div>
                            <Button
                                variant="contained"
                                color="primary"
                                // type="submit"
                                onClick={handleSaveClick}
                                disabled={Object.keys(errors).length}
                            >
                                Save annotation
                            </Button>
                        </div>
                        <div>
                            <Button
                                variant="contained"
                                color="secondary"
                                // type="submit"
                                onClick={() => {
                                    goToRandomAnnotation()
                                }}
                            >
                                Next
                            </Button>
                        </div>
                    </div>


                    {/* <Button variant="contained" color="primary" className="mt-4">
    Submit
</Button> */}
                </form>
            </div>

            {/* Help Modal */}
            <Modal
                open={openHelp}
                onClose={handleHelpClose}
                aria-labelledby="help-modal-title"
                aria-describedby="help-modal-description"
            >
                <Box sx={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '80%', bgcolor: 'background.paper', border: '2px solid #000', boxShadow: 24, p: 4 }}>
                    <Typography id="help-modal-title" variant="h6" component="h2">
                        Detailed Help
                    </Typography>
                    <Typography id="help-modal-description" sx={{ mt: 2 }} component="div">
                        <Typography variant="body1" component="p">
                            <strong>Objective:</strong> Your task is to carefully watch the provided video segment and answer a series of questions that assess the clarity, completeness, and quality of the actions depicted.
                        </Typography>

                        <Typography variant="h6" component="h4" gutterBottom sx={{ mt: 2 }}>
                            Instructions:
                        </Typography>
                        <Typography variant="body1" component="ol" sx={{ pl: 2 }}>
                            <li><strong>Focus on the Details:</strong> Pay close attention to the actions performed in the video, the objects involved, and the overall context.</li>
                            <li><strong>Answer Each Question Thoughtfully:</strong> After watching the video, you will be asked a series of questions. These questions are designed to evaluate different aspects of the video, such as how clearly the action is shown, whether all relevant objects are visible, and if the action is complete from start to finish.</li>
                            <li><strong>Provide Honest and Objective Responses:</strong> Your answers should reflect your true observations and interpretations. There are no right or wrong answers, but your input is critical for assessing the quality of the video content.</li>
                            <li><strong>Consider Revisiting the Video:</strong> If necessary, feel free to replay the video to ensure that your answers are accurate and comprehensive.</li>
                        </Typography>

                        <Typography variant="body1" component="p" sx={{ mt: 2 }}>
                            <strong>Goal:</strong> Your responses will help us understand the quality of this video segment, which will contribute to improving the accuracy and effectiveness of our models.
                        </Typography>
                    </Typography>

                    <Button onClick={handleHelpClose} sx={{ mt: 2 }}>Close</Button>
                </Box>
            </Modal>

            {/* Confirmation Dialog */}
            <Dialog
                open={openDialog}
                onClose={() => handleDialogClose(false)}
            >
                <DialogTitle>Confirm Save</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Are you sure you want to save these changes?
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => handleDialogClose(false)} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={() => handleDialogClose(true)} color="primary" autoFocus>
                        Save
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Snackbar */}
            <Snackbar
                open={openSnackbar}
                autoHideDuration={6000}
                onClose={() => setOpenSnackbar(false)}
            >
                <Alert onClose={() => setOpenSnackbar(false)} severity="success" variant="filled">
                    Annotation saved successfully!
                </Alert>
            </Snackbar>

        </main>
    );
}
