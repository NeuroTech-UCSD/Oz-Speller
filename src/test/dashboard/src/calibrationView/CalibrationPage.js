import React, { useState } from "react";
import FlashingPage from "./FlashingPage";
import SessionForm from "./SessionForm";

const CalibrationPage = () => {
    const [page, setPage] = useState(0)
    return (
        <>
        { page === 0 ? <SessionForm changePage={setPage}/> : <FlashingPage/>}
        </>
    );
}

export default CalibrationPage;