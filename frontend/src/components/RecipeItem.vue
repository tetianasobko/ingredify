<template>
  <div>
    <img :src="imgUrl" alt="dish photo"/>
    <slot>
      <p>Default recipe name</p>
    </slot>
  </div>
</template>

<script>
  export default {
    props: {
      imgUrl: {
        default: "/default_recipe.svg"
      }
    }
  }
</script>

<style scoped>
  div {
    transition: 0.3s;
    border-radius: 10px;
    border: solid gray 2px;
    padding: 20px 0 0 0;
    }
    div:hover {
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
    }
    img {
      display: block;
      width: 60%;
    }
</style>