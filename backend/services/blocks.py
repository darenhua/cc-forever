from services.state import BuildingBlock, CodeFile

snake_code = """var config = {
    type: Phaser.WEBGL,
    width: 640,
    height: 480,
    backgroundColor: '#bfcc00',
    parent: 'phaser-example',
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

var snake;
var food;
var cursors;

//  Direction consts
var UP = 0;
var DOWN = 1;
var LEFT = 2;
var RIGHT = 3;

var game = new Phaser.Game(config);

function preload ()
{
        this.load.setBaseURL('https://cdn.phaserfiles.com/v385');
    this.load.image('food', 'assets/games/snake/food.png');
    this.load.image('body', 'assets/games/snake/body.png');
}

function create ()
{
    var Food = new Phaser.Class({

        Extends: Phaser.GameObjects.Image,

        initialize:

        function Food (scene, x, y)
        {
            Phaser.GameObjects.Image.call(this, scene)

            this.setTexture('food');
            this.setPosition(x * 16, y * 16);
            this.setOrigin(0);

            this.total = 0;

            scene.children.add(this);
        },

        eat: function ()
        {
            this.total++;
        }

    });

    var Snake = new Phaser.Class({

        initialize:

        function Snake (scene, x, y)
        {
            this.headPosition = new Phaser.Geom.Point(x, y);

            this.body = scene.add.group();

            this.head = this.body.create(x * 16, y * 16, 'body');
            this.head.setOrigin(0);

            this.alive = true;

            this.speed = 100;

            this.moveTime = 0;

            this.tail = new Phaser.Geom.Point(x, y);

            this.heading = RIGHT;
            this.direction = RIGHT;
        },

        update: function (time)
        {
            if (time >= this.moveTime)
            {
                return this.move(time);
            }
        },

        faceLeft: function ()
        {
            if (this.direction === UP || this.direction === DOWN)
            {
                this.heading = LEFT;
            }
        },

        faceRight: function ()
        {
            if (this.direction === UP || this.direction === DOWN)
            {
                this.heading = RIGHT;
            }
        },

        faceUp: function ()
        {
            if (this.direction === LEFT || this.direction === RIGHT)
            {
                this.heading = UP;
            }
        },

        faceDown: function ()
        {
            if (this.direction === LEFT || this.direction === RIGHT)
            {
                this.heading = DOWN;
            }
        },

        move: function (time)
        {
            /**
            * Based on the heading property (which is the direction the pgroup pressed)
            * we update the headPosition value accordingly.
            * 
            * The Math.wrap call allow the snake to wrap around the screen, so when
            * it goes off any of the sides it re-appears on the other.
            */
            switch (this.heading)
            {
                case LEFT:
                    this.headPosition.x = Phaser.Math.Wrap(this.headPosition.x - 1, 0, 40);
                    break;

                case RIGHT:
                    this.headPosition.x = Phaser.Math.Wrap(this.headPosition.x + 1, 0, 40);
                    break;

                case UP:
                    this.headPosition.y = Phaser.Math.Wrap(this.headPosition.y - 1, 0, 30);
                    break;

                case DOWN:
                    this.headPosition.y = Phaser.Math.Wrap(this.headPosition.y + 1, 0, 30);
                    break;
            }

            this.direction = this.heading;

            //  Update the body segments and place the last coordinate into this.tail
            Phaser.Actions.ShiftPosition(this.body.getChildren(), this.headPosition.x * 16, this.headPosition.y * 16, 1, this.tail);

            //  Check to see if any of the body pieces have the same x/y as the head
            //  If they do, the head ran into the body

            var hitBody = Phaser.Actions.GetFirst(this.body.getChildren(), { x: this.head.x, y: this.head.y }, 1);

            if (hitBody)
            {
                console.log('dead');

                this.alive = false;

                return false;
            }
            else
            {
                //  Update the timer ready for the next movement
                this.moveTime = time + this.speed;

                return true;
            }
        },

        grow: function ()
        {
            var newPart = this.body.create(this.tail.x, this.tail.y, 'body');

            newPart.setOrigin(0);
        },

        collideWithFood: function (food)
        {
            if (this.head.x === food.x && this.head.y === food.y)
            {
                this.grow();

                food.eat();

                //  For every 5 items of food eaten we'll increase the snake speed a little
                if (this.speed > 20 && food.total % 5 === 0)
                {
                    this.speed -= 5;
                }

                return true;
            }
            else
            {
                return false;
            }
        },

        updateGrid: function (grid)
        {
            //  Remove all body pieces from valid positions list
            this.body.children.each(function (segment) {

                var bx = segment.x / 16;
                var by = segment.y / 16;

                grid[by][bx] = false;

            });

            return grid;
        }

    });

    food = new Food(this, 3, 4);

    snake = new Snake(this, 8, 8);

    //  Create our keyboard controls
    cursors = this.input.keyboard.createCursorKeys();
}

function update (time, delta)
{
    if (!snake.alive)
    {
        return;
    }

    /**
    * Check which key is pressed, and then change the direction the snake
    * is heading based on that. The checks ensure you don't double-back
    * on yourself, for example if you're moving to the right and you press
    * the LEFT cursor, it ignores it, because the only valid directions you
    * can move in at that time is up and down.
    */
    if (cursors.left.isDown)
    {
        snake.faceLeft();
    }
    else if (cursors.right.isDown)
    {
        snake.faceRight();
    }
    else if (cursors.up.isDown)
    {
        snake.faceUp();
    }
    else if (cursors.down.isDown)
    {
        snake.faceDown();
    }

    if (snake.update(time))
    {
        //  If the snake updated, we need to check for collision against food

        if (snake.collideWithFood(food))
        {
            repositionFood();
        }
    }
}

/**
* We can place the food anywhere in our 40x30 grid
* *except* on-top of the snake, so we need
* to filter those out of the possible food locations.
* If there aren't any locations left, they've won!
*
* @method repositionFood
* @return {boolean} true if the food was placed, otherwise false
*/
function repositionFood ()
{
    //  First create an array that assumes all positions
    //  are valid for the new piece of food

    //  A Grid we'll use to reposition the food each time it's eaten
    var testGrid = [];

    for (var y = 0; y < 30; y++)
    {
        testGrid[y] = [];

        for (var x = 0; x < 40; x++)
        {
            testGrid[y][x] = true;
        }
    }

    snake.updateGrid(testGrid);

    //  Purge out false positions
    var validLocations = [];

    for (var y = 0; y < 30; y++)
    {
        for (var x = 0; x < 40; x++)
        {
            if (testGrid[y][x] === true)
            {
                //  Is this position valid for food? If so, add it here ...
                validLocations.push({ x: x, y: y });
            }
        }
    }

    if (validLocations.length > 0)
    {
        //  Use the RNG to pick a random food position
        var pos = Phaser.Math.RND.pick(validLocations);

        //  And place it
        food.setPosition(pos.x * 16, pos.y * 16);

        return true;
    }
    else
    {
        return false;
    }
}
"""

minesweeper_code = """
class Cell
{
    constructor (grid, index, x, y)
    {
        this.grid = grid;

        this.index = index;
        this.x = x;
        this.y = y;

        this.open = false;
        this.bomb = false;

        this.flagged = false;
        this.query = false;
        this.exploded = false;

        //  0 = empty, 1,2,3,4,5,6,7,8 = number of adjacent bombs
        this.value = 0;

        this.tile = grid.scene.make.image({
            key: 'tiles',
            frame: 0,
            x: grid.offset.x + (x * 16),
            y: grid.offset.y + (y * 16),
            origin: 0
        });

        grid.board.add(this.tile);

        this.tile.setInteractive();

        this.tile.on('pointerdown', this.onPointerDown, this);
        this.tile.on('pointerup', this.onPointerUp, this);
    }

    reset ()
    {
        this.open = false;
        this.bomb = false;

        this.flagged = false;
        this.query = false;
        this.exploded = false;

        this.value = 0;

        this.tile.setFrame(0);
    }

    onPointerDown (pointer)
    {
        if (!this.grid.populated)
        {
            this.grid.generate(this.index);
        }

        if (this.open || !this.grid.playing)
        {
            return;
        }

        if (pointer.rightButtonDown())
        {
            if (this.query)
            {
                this.query = false;
                this.tile.setFrame(0);
            }
            else if (this.flagged)
            {
                this.query = true;
                this.flagged = false;
                this.grid.updateBombs(-1);
                this.tile.setFrame(3);
            }
            else if (!this.flagged)
            {
                this.flagged = true;
                this.tile.setFrame(2);
                this.grid.updateBombs(1);
                this.grid.checkWinState();
            }
        }
        else if (!this.flagged && !this.query)
        {
            this.onClick();
        }
    }

    onClick ()
    {
        if (this.bomb)
        {
            this.exploded = true;

            this.grid.gameOver();
        }
        else
        {
            if (this.value === 0)
            {
                this.grid.floodFill(this.x, this.y);
            }
            else
            {
                this.show();
            }

            this.grid.button.setFrame(2);
            this.grid.checkWinState();
        }
    }

    onPointerUp ()
    {
        if (this.grid.button.frame.name === 2)
        {
            this.grid.button.setFrame(0);
        }
    }

    reveal ()
    {
        if (this.exploded)
        {
            this.tile.setFrame(6);
        }
        else if (!this.bomb && (this.flagged || this.query))
        {
            this.tile.setFrame(7);
        }
        else if (this.bomb)
        {
            this.tile.setFrame(5);
        }
        else
        {
            this.show();
        }
    }

    show ()
    {
        const values = [ 1, 8, 9, 10, 11, 12, 13, 14, 15 ];

        this.tile.setFrame(values[this.value]);

        this.open = true;
    }

    debug ()
    {
        const values = [ '⬜️', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣' ];

        if (this.bomb)
        {
            return '💣';
        }
        else
        {
            return values[this.value];
        }
    }
}

class Grid
{
    constructor (scene, width, height, bombs)
    {
        this.scene = scene;

        this.width = width;
        this.height = height;
        this.size = width * height;
        this.offset = new Phaser.Math.Vector2(12, 55);

        this.timeCounter = 0;
        this.bombQty = bombs;
        this.bombsCounter = bombs;

        this.playing = false;
        this.populated = false;

        this.timer = scene.time.addEvent();

        //  0 = waiting to create the grid
        //  1 = playing
        //  2 = game won
        //  3 = game lost
        this.state = 0;

        this.data = [];

        const x = Math.floor((scene.scale.width / 2) - (20 + (width * 16)) / 2);
        const y = Math.floor((scene.scale.height / 2) - (63 + (height * 16)) / 2);

        this.board = scene.add.container(x, y);

        this.digit1;
        this.digit2;
        this.digit3;

        this.time1;
        this.time2;
        this.time3;

        this.button;

        this.createBackground();
        this.createCells();
        this.updateDigits();

        this.button.setInteractive();

        this.button.on('pointerdown', this.onButtonDown, this);
        this.button.on('pointerup', this.onButtonUp, this);
    }

    createCells ()
    {
        let i = 0;

        for (let x = 0; x < this.width; x++)
        {
            this.data[x] = [];

            for (let y = 0; y < this.height; y++)
            {
                this.data[x][y] = new Cell(this, i, x, y);

                i++;
            }
        }
    }

    createBackground ()
    {
        const board = this.board;
        const factory = this.scene.add;

        //  55 added to the top, 8 added to the bottom (63)
        //  12 added to the left, 8 added to the right (20)
        //  cells start at 12 x 55

        const width = this.width * 16;
        const height = this.height * 16;

        //  Top

        board.add(factory.image(0, 0, 'topLeft').setOrigin(0));

        const topBgWidth = (width + 20) - 60 - 56;

        board.add(factory.tileSprite(60, 0, topBgWidth, 55, 'topBg').setOrigin(0));

        board.add(factory.image(width + 20, 0, 'topRight').setOrigin(1, 0));

        //  Sides

        const sideHeight = (height + 63) - 55 - 8;

        board.add(factory.tileSprite(0, 55, 12, sideHeight, 'left').setOrigin(0));
        board.add(factory.tileSprite(width + 20, 55, 8, sideHeight, 'right').setOrigin(1, 0));

        //  Bottom

        board.add(factory.image(0, height + 63, 'botLeft').setOrigin(0, 1));

        const botBgWidth = (width + 20) - 12 - 8;

        board.add(factory.tileSprite(12, height + 63, botBgWidth, 8, 'botBg').setOrigin(0, 1));

        board.add(factory.image(width + 20, height + 63, 'botRight').setOrigin(1, 1));

        //  Bombs Digits

        this.digit1 = factory.image(17, 16, 'digits', 0).setOrigin(0);
        this.digit2 = factory.image(17 + 13, 16, 'digits', 0).setOrigin(0);
        this.digit3 = factory.image(17 + 26, 16, 'digits', 0).setOrigin(0);

        board.add([ this.digit1, this.digit2, this.digit3 ]);

        //  Timer Digits

        const x = (width + 20) - 54;

        this.time1 = factory.image(x, 16, 'digits', 0).setOrigin(0);
        this.time2 = factory.image(x + 13, 16, 'digits', 0).setOrigin(0);
        this.time3 = factory.image(x + 26, 16, 'digits', 0).setOrigin(0);

        board.add([ this.time1, this.time2, this.time3 ]);

        //  Button

        const buttonX = Math.floor(((width + 20) / 2) - 13);

        this.button = factory.image(buttonX, 15, 'buttons', 0).setOrigin(0);

        board.add(this.button);
    }

    updateBombs (diff)
    {
        this.bombsCounter -= diff;

        this.updateDigits();
    }

    updateDigits ()
    {
        const count = Phaser.Utils.String.Pad(this.bombsCounter.toString(), 3, '0', 1);

        this.digit1.setFrame(parseInt(count[0]));
        this.digit2.setFrame(parseInt(count[1]));
        this.digit3.setFrame(parseInt(count[2]));
    }

    onButtonDown ()
    {
        this.button.setFrame(1);
    }

    onButtonUp ()
    {
        if (this.state > 0)
        {
            this.button.setFrame(0);

            this.restart();
        }
    }

    restart ()
    {
        this.populated = false;
        this.playing = false;
        this.bombsCounter = this.bombQty;
        this.state = 0;
        this.timeCounter = -1;
        this.timer.paused = true;

        let location = 0;

        do {

            this.getCell(location).reset();

            location++;

        } while (location < this.size);

        this.updateDigits();

        this.time1.setFrame(0);
        this.time2.setFrame(0);
        this.time3.setFrame(0);
    }

    gameOver ()
    {
        this.playing = false;
        this.state = 3;
        this.timer.paused = true;

        this.button.setFrame(4);

        let location = 0;

        do {

            this.getCell(location).reveal();

            location++;

        } while (location < this.size);
    }

    gameWon ()
    {
        this.playing = false;
        this.state = 2;
        this.timer.paused = true;

        this.button.setFrame(3);
    }

    checkWinState ()
    {
        let correct = 0;
        let location = 0;
        let open = 0;

        do {

            const cell = this.getCell(location);

            if (cell.open)
            {
                open++;
            }

            if (cell.bomb && cell.flagged)
            {
                open++;
                correct++;
            }

            location++;

        } while (location < this.size);

        // console.log('Check', correct, 'out of', this.bombQty, 'open', open, 'of', this.size);

        if (correct === this.bombQty && open === this.size)
        {
            this.gameWon();
        }
    }

    generate (startIndex)
    {
        let qty = this.bombQty;

        const bombs = [];

        do {
            const location = Phaser.Math.Between(0, this.size - 1);

            const cell = this.getCell(location);

            if (!cell.bomb && cell.index !== startIndex)
            {
                cell.bomb = true;

                qty--;

                bombs.push(cell);
            }

        } while (qty > 0);

        bombs.forEach(cell => {

            //  Update the 8 cells around this bomb cell

            const adjacent = this.getAdjacentCells(cell);

            adjacent.forEach(adjacentCell => {

                if (adjacentCell)
                {
                    adjacentCell.value++;
                }
            });
        });

        this.playing = true;
        this.populated = true;
        this.state = 1;

        this.timer.reset({ delay: 1000, callback: this.onTimer, callbackScope: this, loop: true });

        this.debug();
    }

    onTimer ()
    {
        this.timeCounter++;

        if (this.timeCounter < 1000)
        {
            const count = Phaser.Utils.String.Pad(this.timeCounter.toString(), 3, '0', 1);

            this.time1.setFrame(parseInt(count[0]));
            this.time2.setFrame(parseInt(count[1]));
            this.time3.setFrame(parseInt(count[2]));
        }
    }

    getCell (index)
    {
        const pos = Phaser.Math.ToXY(index, this.width, this.height);

        return this.data[pos.x][pos.y];
    }

    getCellXY (x, y)
    {
        if (x < 0 || x >= this.width || y < 0 || y >= this.height)
        {
            return null;
        }

        return this.data[x][y];
    }

    getAdjacentCells (cell)
    {
        return [
            //  Top-Left, Top-Middle, Top-Right
            this.getCellXY(cell.x - 1, cell.y - 1),
            this.getCellXY(cell.x, cell.y - 1),
            this.getCellXY(cell.x + 1, cell.y - 1),

            //  Left, Right
            this.getCellXY(cell.x - 1, cell.y),
            this.getCellXY(cell.x + 1, cell.y),

            //  Bottom-Left, Bottom-Middle, Bottom-Right
            this.getCellXY(cell.x - 1, cell.y + 1),
            this.getCellXY(cell.x, cell.y + 1),
            this.getCellXY(cell.x + 1, cell.y + 1)
        ];
    }

    floodFill (x, y)
    {
        const cell = this.getCellXY(x, y);

        if (cell && !cell.open && !cell.bomb)
        {
            cell.show();

            if (cell.value === 0)
            {
                this.floodFill(x, y - 1);
                this.floodFill(x, y + 1);
                this.floodFill(x - 1, y);
                this.floodFill(x + 1, y);
            }
        }
    }

    debug ()
    {
        for (let y = 0; y < this.height; y++)
        {
            let row = '';

            for (let x = 0; x < this.width; x++)
            {
                let cell = this.data[x][y];

                if (x === 0)
                {
                    row = row.concat(`|`);
                }

                row = row.concat(`${cell.debug()}|`);
            }

            console.log(row);
        }

        console.log('');
    }
}

class Intro extends Phaser.Scene
{
    constructor ()
    {
        super();
    }

    preload ()
    {
        this.load.setBaseURL('https://cdn.phaserfiles.com/v385');
        this.load.setPath('assets/games/minesweeper/');

        this.load.spritesheet('tiles', 'tiles.png', { frameWidth: 16 });
        this.load.spritesheet('digits', 'digits.png', { frameWidth: 13, frameHeight: 23, endFrame: 9 });
        this.load.spritesheet('buttons', 'digits.png', { frameWidth: 26, frameHeight: 26, startFrame: 5 });
        this.load.image('topLeft', 'top-left.png');
        this.load.image('topRight', 'top-right.png');
        this.load.image('topBg', 'top-bg.png');
        this.load.image('botLeft', 'bot-left.png');
        this.load.image('botRight', 'bot-right.png');
        this.load.image('botBg', 'bot-bg.png');
        this.load.image('left', 'left.png');
        this.load.image('right', 'right.png');
        this.load.image('intro', 'intro.png');
        this.load.image('win95', 'win95.png');
    }

    create ()
    {
        this.input.mouse.disableContextMenu();

        this.highlight = this.add.rectangle(0, 334, 800, 70, 0x0182fb).setOrigin(0).setAlpha(0.75);

        this.intro = this.add.image(0, 0, 'intro').setOrigin(0);

        const zone1 = this.add.zone(0, 334, 800, 70).setOrigin(0);
        const zone2 = this.add.zone(0, 411, 800, 70).setOrigin(0);
        const zone3 = this.add.zone(0, 488, 800, 70).setOrigin(0);

        zone1.setInteractive();
        zone2.setInteractive();
        zone3.setInteractive();

        zone1.on('pointerover', () => {
            this.highlight.y = zone1.y;
        });

        zone2.on('pointerover', () => {
            this.highlight.y = zone2.y;
        });

        zone3.on('pointerover', () => {
            this.highlight.y = zone3.y;
        });

        zone1.once('pointerdown', () =>
        {
            this.startGame(9, 9, 10);
        });

        zone2.once('pointerdown', () =>
        {
            this.startGame(16, 16, 40);
        });

        zone3.once('pointerdown', () =>
        {
            this.startGame(16, 30, 99);
        });
    }

    startGame (width, height, bombs)
    {
        this.scene.start('MineSweeper', { width, height, bombs });
    }
}

class MineSweeper extends Phaser.Scene
{
    constructor ()
    {
        super('MineSweeper');
    }

    init (data)
    {
        this.width = data.width;
        this.height = data.height;
        this.bombs = data.bombs;
    }

    create ()
    {
        this.add.image(0, 0, 'win95').setOrigin(0);

        this.grid = new Grid(this, this.width, this.height, this.bombs);
    }
}

const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    backgroundColor: 0x2d2d2d,
    parent: 'phaser-example',
    scene: [ Intro, MineSweeper ]
};

const game = new Phaser.Game(config);
"""

breakout_code = """
class Breakout extends Phaser.Scene
{
    constructor ()
    {
        super({ key: 'breakout' });

        this.bricks;
        this.paddle;
        this.ball;
    }

    preload ()
    {
        this.load.setBaseURL('https://cdn.phaserfiles.com/v385');
        this.load.atlas('assets', 'assets/games/breakout/breakout.png', 'assets/games/breakout/breakout.json');
    }

    create ()
    {
        //  Enable world bounds, but disable the floor
        this.physics.world.setBoundsCollision(true, true, true, false);

        //  Create the bricks in a 10x6 grid
        this.bricks = this.physics.add.staticGroup({
            key: 'assets', frame: [ 'blue1', 'red1', 'green1', 'yellow1', 'silver1', 'purple1' ],
            frameQuantity: 10,
            gridAlign: { width: 10, height: 6, cellWidth: 64, cellHeight: 32, x: 112, y: 100 }
        });

        this.ball = this.physics.add.image(400, 500, 'assets', 'ball1').setCollideWorldBounds(true).setBounce(1);
        this.ball.setData('onPaddle', true);

        this.paddle = this.physics.add.image(400, 550, 'assets', 'paddle1').setImmovable();

        //  Our colliders
        this.physics.add.collider(this.ball, this.bricks, this.hitBrick, null, this);
        this.physics.add.collider(this.ball, this.paddle, this.hitPaddle, null, this);

        //  Input events
        this.input.on('pointermove', function (pointer)
        {

            //  Keep the paddle within the game
            this.paddle.x = Phaser.Math.Clamp(pointer.x, 52, 748);

            if (this.ball.getData('onPaddle'))
            {
                this.ball.x = this.paddle.x;
            }

        }, this);

        this.input.on('pointerup', function (pointer)
        {

            if (this.ball.getData('onPaddle'))
            {
                this.ball.setVelocity(-75, -300);
                this.ball.setData('onPaddle', false);
            }

        }, this);
    }

    hitBrick (ball, brick)
    {
        brick.disableBody(true, true);

        if (this.bricks.countActive() === 0)
        {
            this.resetLevel();
        }
    }

    resetBall ()
    {
        this.ball.setVelocity(0);
        this.ball.setPosition(this.paddle.x, 500);
        this.ball.setData('onPaddle', true);
    }

    resetLevel ()
    {
        this.resetBall();

        this.bricks.children.each(brick =>
        {

            brick.enableBody(false, 0, 0, true, true);

        });
    }

    hitPaddle (ball, paddle)
    {
        let diff = 0;

        if (ball.x < paddle.x)
        {
            //  Ball is on the left-hand side of the paddle
            diff = paddle.x - ball.x;
            ball.setVelocityX(-10 * diff);
        }
        else if (ball.x > paddle.x)
        {
            //  Ball is on the right-hand side of the paddle
            diff = ball.x - paddle.x;
            ball.setVelocityX(10 * diff);
        }
        else
        {
            //  Ball is perfectly in the middle
            //  Add a little random X to stop it bouncing straight up!
            ball.setVelocityX(2 + Math.random() * 8);
        }
    }

    update ()
    {
        if (this.ball.y > 600)
        {
            this.resetBall();
        }
    }
}

const config = {
    type: Phaser.WEBGL,
    width: 800,
    height: 600,
    parent: 'phaser-example',
    scene: [ Breakout ],
    physics: {
        default: 'arcade'
    }
};

const game = new Phaser.Game(config);
"""

snake = BuildingBlock(folder_name="snake",
                      files=[CodeFile(filename="main.py",
                                      code=snake_code)])

minesweeper = BuildingBlock(folder_name="minesweeper",
                            files=[CodeFile(filename="main.py",
                                            code=minesweeper_code)])

breakout = BuildingBlock(folder_name="breakout",
                         files=[CodeFile(filename="main.py",
                                         code=breakout_code)])
