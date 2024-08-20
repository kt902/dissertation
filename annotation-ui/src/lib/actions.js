"use server";

import client from "@/lib/mongodb";

export async function testDatabaseConnection() {
    let isConnected = false;
    try {
        const mongoClient = await client.connect();
        // Send a ping to confirm a successful connection
        await mongoClient.db("admin").command({ ping: 1 });
        console.log(
            "Pinged your deployment. You successfully connected to MongoDB!",
        ); // because this is a server action, the console.log will be outputted to your terminal not in the browser
        return !isConnected;
    } catch (e) {
        console.error(e);
        return isConnected;
    }
}

// import { ObjectId } from 'mongodb'; // If you're using MongoDB's ObjectId

export async function getAnnotationByNarrationId(narrationId) {
    try {
        const mongoClient = await client.connect();
        const database = mongoClient.db(process.env.DB_NAME); // Replace with your actual database name
        const collection = database.collection("annotations"); // Replace with your actual collection name

        // Find the annotation by narrationId
        const annotation = await collection.findOne({ narrationId: narrationId });

        if (!annotation) {
            return {
                success: false,
                message: "No annotation found for the provided narration ID",
            };
        }

        return {
            success: true,
            annotation: {
                ...annotation,
                _id: annotation._id.toString()
            },
        };
    } catch (e) {
        console.error("Error retrieving annotation:", e);
        return {
            success: false,
            message: "Failed to retrieve annotation",
            error: e.message,
        };
    }
}

export async function storeAnnotation(narrationId, annotationData) {
    try {
        const mongoClient = await client.connect();
        const database = mongoClient.db("yourDatabaseName"); // Replace with your actual database name
        const collection = database.collection("annotations"); // Replace with your actual collection name

        // Perform an upsert operation (update if exists, insert if not)
        const result = await collection.updateOne(
            { narrationId: narrationId }, // Filter by narrationId
            {
                $set: annotationData, // Update the document with the new annotation data
            },
            { upsert: true } // Create the document if it doesn't exist
        );

        return {
            success: true,
            upsertedId: string(result.upsertedId), // Return the upsertedId or the existing narrationId
        };
    } catch (e) {
        return {
            success: false,
            message: "Failed to store annotation",
            error: e.message,
        };
    }
}