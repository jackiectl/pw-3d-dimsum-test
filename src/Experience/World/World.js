import Experience from '../Experience.js'
import Environment from './Environment.js'
import Hologram from './Hologram.js'
import DimSumShop from './DimSumShop.js'
import Reflections from './Reflections.js'
import Signs from './Signs.js'
import CounterFood from './CounterFood.js'

export default class World
{
    constructor()
    {
        this.experience = new Experience()
        this.scene = this.experience.scene
        this.resources = this.experience.resources

        // Wait for resources
        this.resources.on('ready', () =>
        {
            // Setup
            this.dimSumShop = new DimSumShop()
            this.signs = new Signs()
            this.counterFood = new CounterFood()
            this.hologram = new Hologram()
            this.reflections = new Reflections()
        })
    }

    update()
    {
        if(this.hologram) {this.hologram.update()}
    }
}