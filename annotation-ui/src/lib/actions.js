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

import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { getServerSession } from "next-auth/next";

export async function getAnnotationByNarrationId(narrationId) {
    try {
        const session = await getServerSession(authOptions);
        const userId = session.user.email;

        const mongoClient = await client.connect();
        const database = mongoClient.db(process.env.DB_NAME); // Replace with your actual database name
        const collection = database.collection("annotation_queue"); // Replace with your actual collection name

        
        // Find the annotation by narrationId
        const annotation = await collection.findOne({ user_id: userId, narration_id: narrationId });

        // Count complete annotations
        const completeCount = await collection.countDocuments({ user_id: userId, status: "complete" });

        // Count all annotations
        const allCount = await collection.countDocuments({ user_id: userId  });


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
            completeCount,
            allCount
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
        const session = await getServerSession(authOptions);
        const userId = session.user.email;

        const mongoClient = await client.connect();
        const database = mongoClient.db(process.env.DB_NAME); // Replace with your actual database name
        const collection = database.collection("annotation_queue"); // Replace with your actual collection name

        // Perform an upsert operation (update if exists, insert if not)
        const result = await collection.updateOne(
            { user_id: userId, narration_id: narrationId }, // Filter by narrationId
            {
                $set: {
                    annotation: annotationData,
                    status: 'complete'
                }, // Update the document with the new annotation data
            },
        );

         // Count pending annotations
         const completeCount = await collection.countDocuments({ user_id: userId, status: "complete" });

         // Count all annotations
         const allCount = await collection.countDocuments({ user_id: userId });
 

        return {
            success: true,
            upsertedId: String(result.upsertedId), // Return the upsertedId or the existing narrationId
            completeCount,
            allCount
        };
    } catch (e) {
        return {
            success: false,
            message: "Failed to store annotation",
            error: e.message,
        };
    }
}

export async function getRandomPendingAnnotation() {
    try {
        const session = await getServerSession(authOptions);
        const userId = session.user.email;

        const mongoClient = await client.connect();
        const database = mongoClient.db(process.env.DB_NAME);
        const collection = database.collection("annotation_queue");

        // Count the total number of pending annotations
        const pendingCount = await collection.countDocuments({ user_id: userId, status: "pending" });
        if (pendingCount === 0) {
            return {
                success: false,
                message: "No pending annotations available",
            };
        }

        // Generate a random skip value
        const randomSkip = Math.floor(Math.random() * pendingCount);

        // Find one random pending annotation
        const annotation = await collection.findOne({ user_id: userId, status: "pending" }, { skip: randomSkip });

        if (!annotation) {
            return {
                success: false,
                message: "Failed to retrieve a random pending annotation",
            };
        }

        return {
            success: true,
            annotation: {
                ...annotation,
                _id: annotation._id.toString(),
            },
        };
    } catch (e) {
        console.error("Error retrieving random pending annotation:", e);
        return {
            success: false,
            message: "Failed to retrieve random pending annotation",
            error: e.message,
        };
    }
}
