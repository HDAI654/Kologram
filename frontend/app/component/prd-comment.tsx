"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import '@/public/entry-styles.css';
import ReactMarkdown from "react-markdown";
import '@/public/scroll-styles.css'

interface commentProps {
  user: string;
  text: string;
}

function PrdComment({ user, text }: commentProps) {
  return (
    <div className="scale-in bg-dark rounded-3 mt-3 mb-3 h-100 w-100" style={{ boxShadow:"0px 0px 20px 2px rgba(221, 66, 66, 0.8)"}}>
        <div className="bg-light w-100 p-1 rounded">
            <h5 className="text-primary mt-1 mb-1">@{user}</h5>
        </div>

        <div className="px-3 mt-1 text-left text-wrap text-light comment-custom-scroll" style={{ maxHeight: "25vh", overflowY: "auto"}}>
            <ReactMarkdown>{text}</ReactMarkdown>
        </div>
    </div>
  );
}

export default PrdComment;
