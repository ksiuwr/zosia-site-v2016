
import { escapeHtml } from "./helpers";

export const apiErrorToast = err => {
    const message = typeof err.body === 'string' || err.body instanceof String
        ? 'ERROR!<br/>' + escapeHtml(err.body)
        : 'There was an internal error with your request.';

    console.log(err);
    return M.toast({
        html: message,
        displayLength: 3000,
        classes: "error"
    });
}

/* messageGen: room => string
* messageGen is a function that generates toast message for specified room
*/
export const roomingSuccessToast = messageGen => room => M.toast({
    html: messageGen(room),
    displayLength: 3000,
    classes: "success"
});
