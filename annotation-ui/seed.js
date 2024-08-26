const { MongoClient } = require("mongodb");
const fs = require("fs");
const path = require("path");
const Papa = require("papaparse");
const dotenv = require("dotenv");

// Load environment variables from .env file
dotenv.config({ path: '.env.local' });

// MongoDB connection setup
const uri = process.env.MONGODB_URI;
const dbName = process.env.DB_NAME;


async function connectToMongoDB() {
    const client = new MongoClient(uri, {
        useNewUrlParser: true,
        useUnifiedTopology: true,
    });

    try {
        await client.connect();
        console.log("Connected to MongoDB");
        const db = client.db(dbName);
        return { client, db };
    } catch (error) {
        console.error("Failed to connect to MongoDB", error);
        process.exit(1);
    }
}

// Function to parse CSV file
function parseCSV(filePath) {
    return new Promise((resolve, reject) => {
        const csvFilePath = path.resolve(filePath);
        const fileContent = fs.readFileSync(csvFilePath, "utf8");

        Papa.parse(fileContent, {
            header: true,
            skipEmptyLines: true,
            complete: function (results) {
                resolve(results.data);
            },
            error: function (error) {
                reject(error);
            },
        });
    });
}

const users = JSON.parse(process.env.USERS);


function distributeItems(items, people) {
    const assignments = {};

    // Initialize assignments for each person
    for (let i = 0; i < people.length; i++) {
        assignments[people[i].email] = [];
    }

    // Distribute each item to 2 people in an alternating fashion
    for (let i = 0; i < items.length; i++) {
        // Determine the first person by cycling through the list
        let person1 = people[i % people.length];

        // Determine the second person by cycling with an offset
        let person2 = people[(i + 1) % people.length];

        // Assign the item to the two selected people
        assignments[person1.email].push(items[i]);
        assignments[person2.email].push(items[i]);
    }

    return assignments;
}

// Main function
(async function main() {
    const { client, db } = await connectToMongoDB();

    const csvFilePath = "./src/data/validations.csv"; // Replace with your actual CSV file path

    try {
        const items = await parseCSV(csvFilePath);

        // Example: filter or select specific items to add
        // const itemsToAdd = parsedData.filter(item => item.narration_id && item.narration); // Simple filter

        // Upsert users
        const usersCollection = db.collection('users');

        for (let index = 0; index < users.length; index++) {
            const { email, password } = users[index];

            const filter = { email: email };
            const update = {
                $set: {
                    email: email,
                    password: password
                }
            };

            const options = { upsert: true };

            const result = await usersCollection.updateOne(filter, update, options);

            if (result.upsertedCount > 0) {
                console.log(`Inserted a new user with email: ${email}`);
            } else {
                console.log(`Updated the user with email: ${email}`);
            }
        }


        // Distribute annotations;
        const itemsPerUser = distributeItems(items, users);

        // Upsert annotations
        const annotationQueueCollection = db.collection("annotation_queue");

        const result = await annotationQueueCollection.deleteMany({});
        console.log(result);

        for (let index = 0; index < users.length; index++) {
            const { email, password } = users[index];

            const items = itemsPerUser[email];

            const annotatedItems = items.map(item => ({
                user_id: email,
                narration_id: item.narration_id,
                // narration: item.narration,
                // url: item.url,
                status: "pending", // Or other fields you'd like to include
                created_at: new Date(),
            }));

            try {
                const result = await annotationQueueCollection.insertMany(annotatedItems);
                console.log(`${result.insertedCount} items inserted successfully`);
            } catch (error) {
                console.error("Failed to insert items", error);
            }
        }


        // await addItemsToAnnotationQueue(userId, itemsToAdd, db);
    } catch (error) {
        console.error("Error processing the CSV file", error);
    } finally {
        await client.close();
        console.log("MongoDB connection closed");
    }
})();
