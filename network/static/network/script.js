document.addEventListener('DOMContentLoaded', function() {

    //add line to contain top tweet
    document.querySelector('.post-container').style.borderTopStyle = 'solid'
    //get user Id to make a post request to like template
    //const user_id = JSON.parse(document.getElementById('user_id').textContent);

    //this fetches all the posts
    fetch('/post/all')
    .then(response => response.json())
    .then(data => {
        console.log(data)
        data.forEach(edit)
        data.forEach(like)
    })

    //this allows for the editing of a tweet
    function edit(context) {
        if(document.querySelector(`#edit-${context.id}`)) {
            document.querySelector(`#edit-${context.id}`).addEventListener('click', () => {
                const close = document.querySelector(`#tweet-${context.id}`)
                close.style.display = 'none'
                const change = document.querySelector(`#edit-tweet-${context.id}`)
                change.style.display = 'block'

                const form = document.querySelector(`#edit-submit-${context.id}`)
                form.addEventListener('click', () => {
                    let new_tweet = document.querySelector(`#edit-area-${context.id}`).value;
                    fetch(`/post/${context.id}`, {
                        method: "PUT",
                        body: JSON.stringify({
                            post: new_tweet
                        })
                    })
                    close.style.display = 'flex'
                    change.style.display = 'none'
                    document.querySelector(`#tweet-${context.id}`).innerHTML = new_tweet
                }) 
            })
        }
    }

    function like(context) {
        if(document.querySelector(`#heart-${context.id}`)) {
            document.querySelector(`#heart-${context.id}`).addEventListener('click', () => {

                let svg = (document.querySelector(`#heart-${context.id}`))
                console.log(context.likes)

                if(svg.style.fill != 'red') {
                    svg.style.fill = 'red'
                    svg.style.stroke = 'red'

                    fetch(`/post/${context.id}`, {
                        method: "PUT",
                        body: JSON.stringify({
                            likes: context.likes + 1
                        })
                    })
                    document.querySelector(`#number-${context.id}`).innerHTML = context.likes + 1 

                }
                else {
                    svg.style.fill = 'none'
                    svg.style.stroke = 'black'

                    fetch(`/post/${context.id}`, {
                        method: "PUT",
                        body: JSON.stringify({
                            likes: context.likes
                        })
                    })
                    document.querySelector(`#number-${context.id}`).innerHTML = context.likes 
                }
            })
        }

            //make put requests for those numbers
            //Find out if json request is true, and have it update the heart
    }
})