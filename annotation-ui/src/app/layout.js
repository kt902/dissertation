import { Inter } from "next/font/google";
import "./globals.css";
import Shell from "./shell";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "EK-100 Quality Annotator",
  description: "An interface for human annotators to add video segement quality annotations to the EPIC Kitchens 100 dataset.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div></div>
        <Shell>
          {children}
        </Shell>
      </body>
    </html>
  );
}
