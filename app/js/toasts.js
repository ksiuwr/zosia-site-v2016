
import { escapeHtml } from './helpers';

export const apiErrorToast = err => {
    console.log(err.body);

    let message = 'There was an internal error with your request.';

    if(typeof(err.body) === 'string' || err.body instanceof String) {
        message = 'ERROR!<br/>' + escapeHtml(err.body)
    }
    else if(err.status == 400 && typeof(err.body) === 'object' && err.body !== null) {
        const infos = Object.entries(err.body).map(e => {
            const msg = Array.isArray(e[1])
                ? e[1].map(escapeHtml).join('<br/>')
                : escapeHtml(e[1]);

            return '<span><strong>' + escapeHtml(e[0]) + '</strong><br/>' + msg + '</span>';
        });

        message = '<p>' + infos.join('<br/><br/>') + '</p>'
    }

    return M.toast({
        html: message,
        displayLength: 3000,
        classes: 'error'
    });
}

/* messageGen: room => string
* messageGen is a function that generates toast message for specified room
*/
export const roomingSuccessToast = messageGen => room => M.toast({
    html: messageGen(room),
    displayLength: 3000,
    classes: 'success'
});
