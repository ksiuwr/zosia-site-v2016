
import React from 'react';

const ModalContext = React.createContext(
    {
        component: null,
        props: {},
        closeModal: () => { },
        openModal: () => { },
    }
);

export const ModalRoot = () => {
    const {component: Component, props} = React.useContext(ModalContext);
    return (Component ? <Component {...props}/> : null)
}

export const useModal = () => {
    const {openModal, closeModal} = React.useContext(ModalContext);
    return [openModal, closeModal]
} 

export const ModalProvider = props => {
    const [context, setContext] = React.useState({
        component: null,
        props: {},
    })

    const closeModal = () => {
        setContext({
            component: null,
            props: {},
        })
    }

    const openModal = (component, props) => {
        setContext({
            component,
            props,
        })
    }

    const modalContext = {...context, closeModal, openModal}

    return (
        <ModalContext.Provider value={modalContext}>
            {props.children}
        </ModalContext.Provider>
    )
}